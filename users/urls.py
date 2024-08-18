from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('register/', views.register, name='register'),  # users/register.html
    path('login/', auth_views.LoginView.as_view(template_name='users/login.html'), name='login'),  # users/login.html
    path('logout/', auth_views.LogoutView.as_view(template_name='users/logout.html'), name='logout'),  # users/logout.html
    path('profile/', views.profile, name='profile'),  # users/profile.html
    path('welcome/', views.welcome, name='welcome'),  # users/welcome.html

    path('password_reset/', auth_views.PasswordResetView.as_view(template_name='users/password_reset.html'), name='password_reset'),  # users/password_reset.html
    path('password_reset_done/', auth_views.PasswordResetDoneView.as_view(template_name='users/password_reset_done.html'), name='password_reset_done'),  # users/password_reset_done.html
    path('password_reset_confirm/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name='users/password_reset_confirm.html'), name='password_reset_confirm'),  # users/password_reset_confirm.html
    path('password_reset_complete/', auth_views.PasswordResetCompleteView.as_view(template_name='users/password_reset_complete.html'), name='password_reset_complete'),  # users/password_reset_complete.html
]
