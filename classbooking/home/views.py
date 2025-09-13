from .forms import SignUpForm
from .forms import SignInForm
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import authenticate
from django.contrib.auth import login
from django.contrib.auth import logout
from django.shortcuts import render
from django.shortcuts import redirect
from django.template import loader

from django.http import HttpResponse


def home(request):
    template = loader.get_template("home/home.html")
    return HttpResponse(template.render())


def auth_login(request):

    if request.user.is_authenticated:
        # already logged in
        messages.info(request, "คุณได้เข้าสู่ระบบเรียบร้อยแล้ว")

        # fetch next parameter from previous page
        next_url = request.GET.get("next", settings.LOGIN_REDIRECT_URL)
        return redirect(next_url)

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

            # login success
            messages.success(request, f"เข้าสู่ระบบสำเร็จ ยินดีต้อนรับครับ คุณ {username}")

            # fetch next parameter from POST request
            next_url = request.POST.get("next", settings.LOGIN_REDIRECT_URL)
            return redirect(next_url)
    else:
        form = SignInForm()

        # change error messages to thai
        form.error_messages["invalid_login"] = (
            "กรุณากรอกชื่อผู้ใช้และรหัสผ่านให้ถูกต้อง โปรดทราบว่าทั้งสองช่องอาจมีการคำนึงถึงตัวพิมพ์เล็กและใหญ่"
        )
        form.error_messages["inactive"] = "บัญชีนี้ไม่ได้ถูกเปิดใช้งานอยู่ กรุณาติดต่อเจ้าหน้าที่"

    return render(request, "home/login.html", {"form": form})


def auth_register(request):

    next_url = request.GET.get("next", settings.LOGIN_REDIRECT_URL)

    if request.user.is_authenticated:
        # already logged in
        messages.info(request, "คุณได้เข้าสู่ระบบเรียบร้อยแล้ว")
        return redirect(next_url)

    if request.method == "POST":
        form = SignUpForm(request.POST)
        if form.is_valid():
            form.save()
            # account created success
            messages.success(request, "สร้างบัญชีสำเร็จแล้ว กรุณาดำเนินการเข้าสู่ระบบ")
            return redirect("auth_login")
    else:
        form = SignUpForm()
    return render(request, "home/register.html", {"form": form})


def auth_logout(request):
    if request.user.is_authenticated:
        logout(request)
        # logout success
        messages.success(request, "ลงชื่อออกสำเร็จ")
        return redirect("auth_logout")
    else:
        return render(request, "home/home.html")


# Create your views here.
