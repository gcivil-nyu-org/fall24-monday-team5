from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from accounts.models import Profile

# from .accounts import CustomUserChangeForm, CustomUserCreationForm
# from .models import Profile, Client, Provider

# class CustomUserAdmin(UserAdmin):
#     add_form = CustomUserCreationForm
#     form = CustomUserChangeForm

#     model = Profile

#     list_display = ('username', 'email', 'is_active',
#                     'is_staff', 'is_superuser', 'last_login',)
#     list_filter = ('is_active', 'is_staff', 'is_superuser')
#     fieldsets = (
#         ('Basic Info', {'fields': ('username', 'email', 'first_name', 'last_name', 'password')}),
#         ('Role', {'fields': ('role',)}),
#         ('Permissions', {'fields': ('is_staff', 'is_active',
#          'is_superuser', 'groups', 'user_permissions')}),
#         ('Dates', {'fields': ('last_login', 'date_joined')})
#     )
#     add_fieldsets = (
#         (None, {
#             'classes': ('wide',),
#             'fields': ('username', 'email', 'password1', 'password2', 'is_staff', 'is_active')}
#          ),
#     )
#     search_fields = ('email',)
#     ordering = ('email',)

# Register your models here.
admin.site.register(Profile)
# admin.site.register(Profile, CustomUserAdmin)
# admin.site.register(Client)
# admin.site.register(Provider)
