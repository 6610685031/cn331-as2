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
        messages.info(request, "You're already logged in!")
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

            # if user doesn't check remember_me button -> make the session expires when the browser is closed
            # normally django will save session token for 14 days (2 weeks)
            if request.POST.get("remember_me"):
                request.session.set_expiry(
                    60 * 60 * 24 * 30
                )  # set session to expires in 30 days
            else:
                request.session.set_expiry(0)  # set to expires after the browser closes
            login(request, authenticate(username=username, password=password))
            messages.success(request, f"Welcome, You are now logged in as {username}")
            return render(request, "home/home.html")
    else:
        form = SignInForm()

        # change error messages to thai
        form.error_messages["invalid_login"] = (
            "กรุณากรอกชื่อผู้ใช้และรหัสผ่านให้ถูกต้อง โปรดทราบว่าทั้งสองช่องอาจมีการคำนึงถึงตัวพิมพ์เล็กและใหญ่"
        )
        form.error_messages["inactive"] = "บัญชีนี้ไม่ได้ถูกเปิดใช้งานอยู่ กรุณาติดต่อเจ้าหน้าที่"
    return render(request, "home/login.html", {"form": form})


def auth_register(request):
    if request.user.is_authenticated:
        messages.info(request, "You're already logged in!.")
        return render(request, "home/home.html")

    if request.method == "POST":
        form = SignUpForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(
                request, "Account created successfully! Please proceed to login."
            )
            return redirect("auth_login")
    else:
        form = SignUpForm()
    return render(request, "home/register.html", {"form": form})


def auth_logout(request):
    if request.user.is_authenticated:
        logout(request)
        messages.success(request, "Logout successful!")
        return redirect("auth_logout")
    else:
        return render(request, "home/home.html")


# Create your views here.
