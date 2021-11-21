from django.http import HttpResponse
from django.shortcuts import render


# Create your views here.
def dashboard(request):
    context = {'page_name': 'Register'}
    return render(request, 'application/dashboard.html', context)
