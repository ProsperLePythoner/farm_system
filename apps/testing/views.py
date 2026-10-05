from multiprocessing import context

from django.template.loader import get_template

from django.template import loader
from django.http import HttpResponse

from django.http import HttpResponseRedirect
from django.shortcuts import render
from .forms import NameForm

def testing(request):
    print("Testing the 'testing' view...\n\n\n")

    template = loader.get_template("testing/tests.html")
    return HttpResponse(template.render({
        'name': 'Prosper.dev'
    }, request))

def say_hello(request, name):
    return HttpResponse(f"Hello, {name}. How are ya? 😊")

def get_name(request):
    # if this is a POST request we need to process the form data
    if request.method == "POST":
        # create a form instance and populate it with data from the request:
        form = NameForm(request.POST)
        # check whether it's valid:
        if form.is_valid():
            # process the data in form.cleaned_data as required
            # ...
            # redirect to a new URL:
            user_name = form.cleaned_data['your_name']
            return HttpResponseRedirect(f"testing/{user_name}/")

    # if a GET (or any other method) we'll create a blank form
    else:
        form = NameForm()

    return render(request, "name_form.html", {"form": form})

"""
ERROR LOG:......


Forbidden (403)

CSRF verification failed. Request aborted.
Help

Reason given for failure:

    CSRF token missing.
    

In general, this can occur when there is a genuine Cross Site Request Forgery, or when Django’s CSRF mechanism has not been used correctly. For POST forms, you need to ensure:

    Your browser is accepting cookies.
    The view function passes a request to the template’s render method.
    In the template, there is a {% csrf_token %} template tag inside each POST form that targets an internal URL.
    If you are not using CsrfViewMiddleware, then you must use csrf_protect on any views that use the csrf_token template tag, as well as those that accept the POST data.
    The form has a valid CSRF token. After logging in in another browser tab or hitting the back button after a login, you may need to reload the page with the form, because the token is rotated after a login.

You’re seeing the help section of this page because you have DEBUG = True in your Django settings file. Change that to False, and only the initial error message will be displayed.

You can customize this page using the CSRF_FAILURE_VIEW setting.
"""