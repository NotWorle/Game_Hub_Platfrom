from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import RegistrationForm, LoginForm, RoleUpgradeRequestForm, FormInfor
from django.http import HttpResponseForbidden, HttpResponse 
from .models import CustomUser
from games.models import Game
from django.core.mail import send_mail
import random, os
from django.conf import settings

def redirect_base_on_role(user):
    if user.is_superuser or user.role == 'admin':
    # Đăng nhập người dùng và chuyển hướng đến admin
        user.role = 'admin'
        user.save()
        return redirect('/admin/')  # Trang admin của Django
    else:
        return redirect('home')  # Trang mặc định nếu không phải các vai trò trên  # Nếu không khớp vai trò nào, mặc định là home

def login_view(request):
    if request.method == 'POST':
        form = LoginForm(data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)

            if user is not None:
                login(request, user)
                messages.success(request, f"Welcome, {user.username}")
                return redirect_base_on_role(user)
            else:
                form.add_error(None, 'Invalid username or password')  # Thêm thông báo lỗi nếu thông tin sai
    else:
        form = LoginForm()
    return render(request, 'login.html', {'form': form})


def register(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)  # Đăng nhập người dùng sau khi đăng ký
            messages.success(request, f"Welcome, {user.username}")
            return redirect_base_on_role(user)
        else:
            messages.error(request, "Invalid information")
    else:
        form = RegistrationForm()
    return render(request, 'home.html', {'form': form})

@login_required
def logout_view(request):
    logout(request)
    return redirect('home')

@login_required
def upgrade_role(request):
    if not request.user.is_authenticated:
        # Nếu người dùng chưa đăng nhập
        return render(request, 'ErrorLogin.html')
    
    user = request.user  # Lấy người dùng đã đăng nhập
    if request.method == 'POST':
        form = RoleUpgradeRequestForm(request.POST)
        if form.is_valid():
            # Lưu yêu cầu nâng cấp vai trò
            user.requested_role = form.cleaned_data['requested_role']
            user.request_status = CustomUser.STATUS_PENDING
            user.save()
            messages.success(request, "Your role upgrade request has been submitted.")
            return redirect('home')  # Redirect đến trang home hoặc trang phù hợp
    else:
        form = RoleUpgradeRequestForm()

    return render(request, 'role_upgrade.html', {'form': form})



@login_required
def information(request):
    user = request.user
    if request.method == "POST":
        form = FormInfor(request.POST, request.FILES, instance=user)
        name = os.path.basename(user.avatar.name)
        parent = os.path.dirname(user.avatar.path)
        if form.is_valid():
            if 'avatar' in request.FILES and name != 'gojo.jpg':
                path = os.path.join(parent, name)
                if os.path.exists(path):
                    os.remove(path)
            form.save()
    return redirect('home')


def reset_password(request):
    return render(request, 'password_reset.html')


def home(request):
    game = Game.objects.all()
    login_form=LoginForm()
    register_form=RegistrationForm()
    if request.method == "POST":
        if 'login' in request.POST:
            login_form = LoginForm(data = request.POST)
            if login_form.is_valid():
                username = login_form.cleaned_data.get('username')
                password = login_form.cleaned_data.get('password')
                user =authenticate(username=username, password=password)

                if user is not None:
                    login(request, user)
                    messages.success(request, f"Welcome, {user.username}")
                    return redirect_base_on_role(user)
                else:
                    messages.error(request, "Invalid username or password")
            else:
                messages.error(request, "Invalid username or password")
        elif 'register' in request.POST:
            register_form = RegistrationForm(request.POST)
            if register_form.is_valid():
                user = register_form.save()
                backend = 'django.contrib.auth.backends.ModelBackend'
                login(request, user, backend=backend)
                messages.success(request, f"Welcome, {user.username}")
                return redirect_base_on_role(user)
            else:
                messages.error(request, "Invalid information")
    else:
        login_form=LoginForm()
        register_form=RegistrationForm()

    return render(request, 'home.html', {
        'login_form': login_form,
        'register_form': register_form,
        'games': game
    })

def error(request):
    return render(request, 'error.html')

def ErrorLogin(request):
    return render(request, 'ErrorLogin.html')

def ErrorTruyCap(request):
    return render(request, 'ErrorTruyCap.html')
