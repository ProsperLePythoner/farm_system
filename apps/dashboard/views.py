from django.shortcuts import render
from django.http import HttpResponse
from django.template.loader import get_template

# Create your views here.
'''
def dashboard(request):
    return HttpResponse("Dashboard")
'''

# Doing some experimenting over here...
def dashboard(request):
    template = get_template('templates/base/base.html')
    return HttpResponse(template.render({
        'title': 'Dashboard',
        'developer_name': 'Prosper.dev',
        'developer_email': 'prosperlukamaja@gmail.com',
    }))