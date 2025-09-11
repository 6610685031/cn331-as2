from .forms import SignUpForm
from django.contrib.auth import authenticate
from django.shortcuts import render
from django.template import loader
from django.http import HttpResponse


def home(request):
    template = loader.get_template("home/home.html")
    return HttpResponse(template.render())


def login(request):
    if request.method == "POST":
        f_user = request.POST.get("username")
        f_passwrd = request.POST.get("password")

        user = authenticate(username=f_user, password=f_passwrd)
        if user is not None:
            return HttpResponse("Login successfully.")
            # A backend authenticated the credentials
        else:
            return HttpResponse("Failed to log in.")
            # No backend authenticated the credentials

    template = loader.get_template("home/login.html")
    return HttpResponse(template.render())


def signup(request):
    if request.method == "POST":
        form = SignUpForm(request.POST)
        if form.is_valid():
            form.save()
            return HttpResponse("Account created successfully! You can now login.")
    else:
        form = SignUpForm()
    return render(request, "home/signup.html", {"form": form})


# Create your views here.
