from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm, PasswordChangeForm, PasswordResetForm
from .models import CustomUser
import os, uuid
from django.conf import settings

class RegistrationForm(UserCreationForm):
    password1 = forms.CharField(
        label="Password",
        widget=forms.PasswordInput,
    )
    password2 = forms.CharField(
        label="Confirm Password",
        widget=forms.PasswordInput,
    )
    requested_role = forms.ChoiceField(
        choices=CustomUser.ROLE_CHOICES,  # Tải các lựa chọn từ model CustomUser
        label="Select Role",
        widget=forms.Select,
    )

    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'password1', 'password2', 'requested_role']  # Bao gồm trường requested_role

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Loại bỏ help texts khỏi tất cả các trường
        for field in self.fields.values():
            field.help_text = ""
    
    def clean(self):
        cleaned_data = super().clean()
        requested_role = cleaned_data.get('requested_role')

        # Kiểm tra nếu requested_role không hợp lệ
        if requested_role not in dict(CustomUser.ROLE_CHOICES):
            raise forms.ValidationError({'requested_role': 'Invalid role selection.'})

        return cleaned_data
class LoginForm(AuthenticationForm):
    class Meta:
        model = CustomUser
        fields = ['username', 'password']

class RoleUpgradeRequestForm(forms.Form):
    requested_role = forms.ChoiceField(
        choices=[(CustomUser.ROLE_DEVELOPER, 'Developer'), (CustomUser.ROLE_DESIGNER, 'Designer'), (CustomUser.ROLE_DEV_DES, 'Dev/Des')],
        label="Request Role Upgrade",
    )
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Loại bỏ help_text mặc định từ tất cả các trường
        for field in self.fields.values():
            field.help_text = ""
    
    def clean_requested_role(self):
        """Kiểm tra sự hợp lệ của requested_role"""
        requested_role = self.cleaned_data.get('requested_role')
        
        if requested_role not in [CustomUser.ROLE_DEVELOPER, CustomUser.ROLE_DESIGNER, CustomUser.ROLE_DEV_DES]:
            raise forms.ValidationError('Invalid role selection.')
        
        return requested_role

    def clean(self):
        """Phương thức này sẽ kiểm tra nếu trường requested_role không được chọn"""
        cleaned_data = super().clean()
        requested_role = cleaned_data.get('requested_role')

        if not requested_role:
            raise forms.ValidationError({'requested_role': 'You must select a role to upgrade.'})

        return cleaned_data
    

class FormInfor(forms.ModelForm):
    class Meta:
        model = CustomUser 
        fields = ('first_name', 'last_name', 'email','avatar')


    def clean_avatar(self):
        avatar = self.cleaned_data.get('avatar')
        if avatar == self.instance.avatar.name:
            print("báo lỗi trùng tên")
            forms.ValidationError("Đổi lại tên tệp avatar")
        elif avatar:
            # Lấy phần mở rộng của file (đuôi file)
            _, image_extension = os.path.splitext(avatar.name)

            # Tạo tên mới ngẫu nhiên
            new_image_name = f"{uuid.uuid4().hex}{image_extension.lower()}"

            # Cập nhật tên mới cho file avatar
            avatar.name = os.path.join('avatar', new_image_name)

        return avatar  # Django sẽ tự động lưu vào MEDIA_ROOT
   



class CustomPasswordResetForm(PasswordResetForm):
    username = forms.CharField(max_length=150, required=True, label="Username")

    def __init__(self, *args, **kwargs):
        # Gọi constructor của lớp cha để xử lý các tham số như `initial`
        super().__init__(*args, **kwargs)
        
    def clean(self):
        cleaned_data = super().clean()
        email = cleaned_data.get('email')
        username = cleaned_data.get('username')

        if not CustomUser.objects.filter(username=username, email=email).exists():
            self.add_error('username', "Không tìm thấy người dùng với username và email này.")
            self.add_error('email', "Vui lòng kiểm tra lại email.")

        return cleaned_data
