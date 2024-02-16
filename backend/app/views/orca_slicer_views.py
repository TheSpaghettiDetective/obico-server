from oauth2_provider.models import get_access_token_model
from django.http import  JsonResponse
from django.shortcuts import render

def welcome(request):
    return render(request, 'orca_slicer_welcom.html')