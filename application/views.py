from django.http import HttpResponse
from django.shortcuts import render
from application.functions import create_context


# Create your views here.
def dashboard(request):
    context = create_context(request)
    return render(request, 'application/dashboard.html', context)
