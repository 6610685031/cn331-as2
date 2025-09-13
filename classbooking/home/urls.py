from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("login/", views.auth_login, name="auth_login"),
    path("logout/", views.auth_logout, name="auth_logout"),
    path("register/", views.auth_register, name="auth_register"),
]
