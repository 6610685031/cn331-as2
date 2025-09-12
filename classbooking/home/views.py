from .forms import SignUpForm
from .forms import SignInForm
from django.contrib import messages
from django.contrib.auth import authenticate
from django.contrib.auth import login
from django.contrib.auth import logout
from django.shortcuts import render
from django.shortcuts import redirect
from django.template import loader

from django.http import HttpResponse
from django.urls import reverse


def home(request):
    template = loader.get_template("home/home.html")
    return HttpResponse(template.render())


def auth_login(request):
    if request.user.is_authenticated:
        messages.success(request, "You're already logged in!.")
        return render(request, "home/home.html")

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
            messages.success(
                request, f"Login successful!. You are now logged in as {username}"
            )
            return render(request, "home/home.html")
    else:
        form = SignInForm()

        # change error messages to thai
        form.error_messages["invalid_login"] = (
            "กรุณากรอกชื่อผู้ใช้และรหัสผ่านให้ถูกต้อง โปรดทราบว่าทั้งสองช่องอาจมีการคำนึงถึงตัวพิมพ์เล็กและใหญ่"
        )
        form.error_messages["inactive"] = "บัญชีนี้ไม่ได้ถูกเปิดใช้งานอยู่ กรุณาติดต่อเจ้าหน้าที่"
    return render(request, "home/login.html", {"form": form})


def auth_signup(request):
    if request.user.is_authenticated:
        messages.success(request, "You're already logged in!.")
        return render(request, "home/home.html")

    if request.method == "POST":
        form = SignUpForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(
                request, "Account created successfully! You can now login."
            )
            return redirect("auth_signup")
    else:
        form = SignUpForm()
    return render(request, "home/signup.html", {"form": form})


def auth_logout(request):
    if request.user.is_authenticated:
        logout(request)
        messages.success(request, "Logout successful!.")
        return redirect("auth_logout")
    else:
        return render(request, "home/home.html")


# Create your views here.
