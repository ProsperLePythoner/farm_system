from multiprocessing import context

from django.template.loader import get_template

from django.template import loader
from django.http import HttpResponse

def testing(request):
    print("Testing the 'testing' view...\n\n\n")

    template = loader.get_template("templates/testing/tests.html")
    return HttpResponse(template.render({
        'name': 'Prosper.dev'
    }, request))

def say_hello(request, name):
    return HttpResponse(f"Hello, {name}. How are ya? 😊")