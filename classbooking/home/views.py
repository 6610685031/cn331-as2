from .forms import SignUpForm
from .forms import SignInForm
from django.contrib.auth import authenticate
from django.contrib.auth import login
from django.contrib.auth import logout
from django.shortcuts import render
from django.template import loader
from django.http import HttpResponse


def home(request):
    template = loader.get_template("home/home.html")
    return HttpResponse(template.render())


def auth_login(request):
    if request.method == "POST":

        # data argument must be used in order for the form to be valid.
        # see https://stackoverflow.com/questions/45824046/djangos-authentication-form-is-always-not-valid
        form = SignInForm(request=request, data=request.POST)

        # is_valid() already checks for correct username and password
        # it also checks if the form = None or not, so no need for double-checking it
        if form.is_valid():
            username = form.cleaned_data.get("username")
            password = form.cleaned_data.get("password")
            login(request, authenticate(username=username, password=password))
            return HttpResponse(
                f"Login successful!. You are now logged in as {username}"
            )
        else:
            return HttpResponse(
                "Please enter a correct username and password. Note that both fields may be case-sensitive."
            )

    form = SignInForm()
    return render(request, "home/login.html", {"form": form})


def auth_signup(request):
    if request.method == "POST":
        form = SignUpForm(request.POST)
        if form.is_valid():
            form.save()
            return HttpResponse("Account created successfully! You can now login.")
    else:
        form = SignUpForm()
        return render(request, "home/signup.html", {"form": form})


def auth_logout(request):
    logout(request)
    return HttpResponse("Logout successful!.")


# Create your views here.
