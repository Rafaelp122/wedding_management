from django.shortcuts import render


def home(request):
    return render(request, "pages/home.html")


def contact_us(request):
    return render(request, "pages/contact_us.html")
