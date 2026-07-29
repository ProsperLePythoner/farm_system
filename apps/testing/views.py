from multiprocessing import context

from django.template.loader import get_template
from django.template import loader
from django.http import HttpResponse

def testing(request):
    print("Testing the 'testing' view...")

    template = loader.get_template("templates/testing/tests.html")
    return HttpResponse(template.render({
        'template_name': "templates/testing/tests.html",
        'developer': 'Prosper.dev',
    }, request))