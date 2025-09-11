from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.forms import AuthenticationForm
from crispy_forms.helper import FormHelper


class SignInForm(AuthenticationForm):
    username = forms.CharField(max_length=150, required=True, label="ชื่อผู้เข้าใช้ของคุณ")
    password = forms.CharField(
        required=True, label="รหัสผ่าน", widget=forms.PasswordInput
    )

    class Meta:
        model = User
        fields = ["username", "email"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.helper = FormHelper()
        self.helper.form_method = "post"
        self.fields["username"].widget.attrs.update(
            {"placeholder": "กรอกชื่อผู้เข้าใช้ของคุณ"}
        )
        self.fields["password"].widget.attrs.update({"placeholder": "กรอกรหัสผ่านของคุณ"})


class SignUpForm(UserCreationForm):
    username = forms.CharField(
        max_length=150, required=True, label="ชื่อผู้เข้าใช้ของคุณ (ใช้สำหรับการเข้าระบบ)"
    )
    email = forms.EmailField(required=True, label="ที่อยู่อีเมล")
    password1 = forms.CharField(
        required=True, label="รหัสผ่าน", widget=forms.PasswordInput
    )
    password2 = forms.CharField(
        required=True, label="ยืนยันรหัสผ่าน", widget=forms.PasswordInput
    )

    class Meta:
        model = User
        fields = ["username", "email", "password1", "password2"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.helper = FormHelper()
        self.helper.form_method = "post"
        self.fields["username"].widget.attrs.update(
            {"placeholder": "กรอกชื่อผู้เข้าใช้ของคุณ"}
        )
        self.fields["email"].widget.attrs.update({"placeholder": "กรอกอีเมล์ของคุณ"})
        self.fields["password1"].widget.attrs.update({"placeholder": "กรอกรหัสผ่านของคุณ"})
        self.fields["password2"].widget.attrs.update({"placeholder": "ยืนยันรหัสผ่านอีกครั้ง"})
