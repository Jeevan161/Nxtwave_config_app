from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test


def is_staff_user(user):
    return user.is_staff


@login_required
def home_redirect(request):
    # Check if user is a staff member
    if request.user.is_staff:
        return redirect('gamma_dashboard')  # Replace with your actual gamma dashboard URL name
    else:
        return redirect('beta/dashboard')  # Replace with your actual beta dashboard URL name


def access_denied(request):
    return render(request, 'Beta/access_denied.html')


@login_required
def beta_dashboard(request):
    return render(request, 'Beta/beta_dashboard.html')


@login_required
@user_passes_test(is_staff_user, login_url='access_denied')
def gamma_dashboard(request):
    return render(request, 'Beta/gamma_dashboard.html')


def register_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        email = request.POST['email']
        print(password)
        # Create the user with `is_active=False` for admin approval
        user = User.objects.create_user(username=username, password=password, email=email)
        user.is_active = False  # Require admin approval
        user.save()
        messages.success(request, 'Registration successful. Waiting for admin approval.')
        return redirect('login')
    return render(request, 'Beta/register.html')


def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        try:
            # Attempt to retrieve the user by username
            user = User.objects.get(username=username)

            # Check if the password is correct
            if user.check_password(password):
                # If the password is correct, check if the user is active
                if user.is_active:
                    login(request, user)
                    if user.is_staff:
                        return redirect('/')
                    else:
                        return redirect('/')
                else:
                    # User exists and password is correct, but account is inactive
                    return render(request, 'Beta/account_not_approved.html')
            else:
                # Password does not match
                messages.error(request, 'Invalid credentials')

        except User.DoesNotExist:
            # User with the given username does not exist
            messages.error(request, 'Invalid credentials')

    return render(request, 'Beta/login.html')


def logout_view(request):
    logout(request)
    return redirect('login')


@login_required
def content_developer_dashboard(request):
    return render(request, 'Beta/cd.html')


@login_required
def configurator_dashboard(request):
    return render(request, 'Beta/configurator.html')
