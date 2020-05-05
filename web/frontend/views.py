from django.shortcuts import render

def index(request):
    return render(request, 'frontend/index.html')

def prints(request):
    print("prints page")
    return render(request, 'frontend/index.html')