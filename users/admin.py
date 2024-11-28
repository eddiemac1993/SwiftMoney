from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser

class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = (
        'username', 
        'first_name', 
        'last_name', 
        'phone_number', 
        'house_number', 
        'business_location', 
        'is_approved', 
        'is_driver'  # Added 'is_driver' to display
    )
    list_filter = (
        'is_approved', 
        'is_staff', 
        'is_superuser', 
        'is_driver'  # Added 'is_driver' to filter
    )
    search_fields = (
        'username', 
        'first_name', 
        'last_name', 
        'phone_number', 
        'business_location'
    )
    ordering = ('username',)
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal Info', {'fields': ('first_name', 'last_name', 'phone_number', 'house_number', 'business_location', 'profile_pic')}),
        ('Permissions', {'fields': ('is_staff', 'is_superuser', 'is_approved', 'is_driver', 'groups', 'user_permissions')}),  # Added 'is_driver'
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': (
                'username', 
                'first_name', 
                'last_name', 
                'phone_number', 
                'house_number', 
                'business_location', 
                'password1', 
                'password2', 
                'is_staff', 
                'is_superuser', 
                'is_approved', 
                'is_driver'  # Added 'is_driver' to the add form
            ),
        }),
    )

admin.site.register(CustomUser, CustomUserAdmin)
