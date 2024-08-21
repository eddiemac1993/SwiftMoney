from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from .forms import CustomUserCreationForm
from django.core.mail import send_mail
from django.conf import settings
from .forms import ProfileForm  # Assuming you have a form for updating profiles
from .models import CustomUser

def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save()
            login(request, user)
            # Send notification email to admin
            send_mail(
                'New User Registration',
                f'A new user {user.username} has registered.',
                settings.DEFAULT_FROM_EMAIL,
                [settings.ADMIN_EMAIL],
                fail_silently=False,
            )
            return redirect('welcome')
    else:
        form = CustomUserCreationForm()
    return render(request, 'users/register.html', {'form': form})

def welcome(request):
    return render(request, 'users/welcome.html')

@login_required
def profile(request):
    user = request.user
    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES, instance=user)
        if form.is_valid():
            form.save()
            return redirect('profile')  # Redirect to the profile page after successful update
    else:
        form = ProfileForm(instance=user)

    return render(request, 'users/profile.html', {'form': form})
