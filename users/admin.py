from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser

class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = ('username', 'first_name', 'last_name', 'phone_number', 'house_number', 'business_location', 'is_approved')
    list_filter = ('is_approved', 'is_staff', 'is_superuser')
    search_fields = ('username', 'first_name', 'last_name', 'phone_number', 'business_location')
    ordering = ('username',)
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal Info', {'fields': ('first_name', 'last_name', 'phone_number', 'house_number', 'business_location', 'profile_pic')}),
        ('Permissions', {'fields': ('is_staff', 'is_superuser', 'is_approved', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'first_name', 'last_name', 'phone_number', 'house_number', 'business_location', 'password1', 'password2', 'is_staff', 'is_superuser', 'is_approved'),
        }),
    )

admin.site.register(CustomUser, CustomUserAdmin)
