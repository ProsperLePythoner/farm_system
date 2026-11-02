"""Build a tiny Material Symbols font containing only the icons the templates use.

WHAT THIS DOES
    The site renders icons with Material Symbols *ligatures*:
    ``<span class="material-symbols-outlined">dashboard</span>``. The complete
    font is about 4 MB, so every first-time visitor used to download 4 MB to
    show roughly 20 icons. This script keeps only the glyphs for icons that
    are actually referenced in ``templates/`` and ``static/js/`` and pins the
    variable axes to the values ``static/css/base.css`` uses
    (FILL 0, wght 400, GRAD 0, opsz 20), which brings the file to a few KB.

WHEN TO RUN IT
    Whenever you use a NEW icon name in a template, run, from the project root:

        pip install fonttools brotli
        python tools/subset_icons.py

    Then commit the regenerated files.

    If you ever want a different icon style (filled icons, other weights),
    change the AXES below and CSS ``font-variation-settings`` together.

INPUT / OUTPUT
    Input : tools/material-symbols-outlined.full.woff2  (the complete font)
    Output: static/fonts/material-symbols/material-symbols-subset.woff2
            static/fonts/material-symbols/icons.txt (list of included icons)
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SOURCE = ROOT / "tools" / "material-symbols-outlined.full.woff2"
OUT_DIR = ROOT / "static" / "fonts" / "material-symbols"
OUTPUT = OUT_DIR / "material-symbols-subset.woff2"
MANIFEST = OUT_DIR / "icons.txt"

# Must match font-variation-settings in static/css/base.css.
AXES = {"FILL": 0, "wght": 400, "GRAD": 0, "opsz": 20}

# Icons referenced indirectly (not as literal text in a template).
EXTRA_ICONS: set[str] = set()

SCAN_PATTERNS = (
    # <span class="material-symbols-outlined ...">icon_name</span>
    re.compile(r'material-symbols-outlined[^>]*>\s*([a-z][a-z0-9_]*)\s*<'),
    # {% include "base/icon.html" with icon="icon_name" %}
    re.compile(r'''\bicon=["']([a-z][a-z0-9_]*)["']'''),
    # icon.html maps {% else %}{{ icon }} - literal fallbacks inside it
    re.compile(r'''\{%\s*else\s*%\}\s*([a-z][a-z0-9_]*)\s*\{%'''),
)


def find_used_icons() -> set[str]:
    """Collect icon names referenced by templates and JavaScript."""
    names: set[str] = set(EXTRA_ICONS)
    files = list((ROOT / "templates").rglob("*.html"))
    files += list((ROOT / "apps").rglob("templates/**/*.html"))
    files += list((ROOT / "static" / "js").rglob("*.js"))
    for path in files:
        text = path.read_text(encoding="utf-8")
        for pattern in SCAN_PATTERNS:
            names.update(pattern.findall(text))
    # icon.html renders {{ icon }} verbatim except for the "harvest" alias.
    names.discard("harvest")
    names.add("agriculture")
    return names


def find_ligature_glyph(font, name):
    """Return the glyph name that the ligature ``name`` turns into, or None.

    Material Symbols stores each icon as an OpenType ligature: the letters of
    the icon's name (d-a-s-h-b-o-a-r-d) are substituted by one icon glyph. This
    reads that substitution table directly, so only fontTools is required.
    """
    cmap = font.getBestCmap()
    try:
        letters = [cmap[ord(ch)] for ch in name]
    except KeyError:
        return None
    for lookup in font["GSUB"].table.LookupList.Lookup:
        for subtable in lookup.SubTable:
            if lookup.LookupType == 7:  # "extension" wrapper around the real table
                subtable = subtable.ExtSubTable
            ligatures = getattr(subtable, "ligatures", None)
            if not ligatures:
                continue
            for ligature in ligatures.get(letters[0], []):
                if ligature.Component == letters[1:]:
                    return ligature.LigGlyph
    return None


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("--source", type=Path, default=SOURCE)
    parser.add_argument("--output", type=Path, default=OUTPUT)
    args = parser.parse_args()

    try:
        from fontTools import subset
        from fontTools.ttLib import TTFont
        from fontTools.varLib import instancer
    except ImportError:
        print("Install build tools first: pip install fonttools brotli")
        return 1

    if not args.source.exists():
        print(f"Source font not found: {args.source}")
        return 1

    icons = sorted(find_used_icons())
    print(f"{len(icons)} icons in use: {', '.join(icons)}")

    # 1. Look up which glyph each icon name turns into. A name with no
    #    ligature is not a real icon (typo, or not in this font version).
    font = TTFont(str(args.source))
    ligature_glyphs: dict[str, str] = {}
    for name in icons:
        glyph = find_ligature_glyph(font, name)
        if glyph is None:
            print(f"ERROR: '{name}' is not an icon in this font (typo, or a newer icon name?).")
            return 1
        ligature_glyphs[name] = glyph

    # 2. Pin variable axes -> static font (drops all variation data).
    if "fvar" in font:
        font = instancer.instantiateVariableFont(font, AXES, inplace=False)

    # 3. Keep only: the letters used in icon names (so the ligature rule can
    #    match), and the ligature glyphs themselves. Layout closure is
    #    disabled on purpose - otherwise fontTools re-adds every ligature
    #    whose letters are present, i.e. all ~3,000 icons.
    letters = sorted({ch for name in icons for ch in name})
    options = subset.Options()
    options.layout_features = ["rlig", "rclt", "liga", "calt"]
    options.layout_closure = False
    options.glyph_names = False
    options.notdef_outline = True
    options.name_IDs = [1, 2]
    options.flavor = "woff2"
    subsetter = subset.Subsetter(options)
    subsetter.populate(
        unicodes=[ord(ch) for ch in letters],
        glyphs=sorted(set(ligature_glyphs.values())),
    )
    subsetter.subset(font)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    font.flavor = "woff2"
    font.save(str(args.output))

    # 4. Verify the OUTPUT font: every icon name must still map to a ligature.
    check = TTFont(str(args.output))
    for name in icons:
        if find_ligature_glyph(check, name) is None:
            print(f"ERROR: '{name}' is missing from the subset font.")
            return 1

    MANIFEST.write_text("\n".join(icons) + "\n", encoding="utf-8")
    size_kb = args.output.stat().st_size / 1024
    src_kb = args.source.stat().st_size / 1024
    print(f"OK: {args.output} = {size_kb:.1f} KB (was {src_kb:,.0f} KB)")
    return 0


if __name__ == "__main__":
    sys.exit(main())