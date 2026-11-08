from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import user

@admin.register(user)
class CustomUserAdmin(UserAdmin):
    model = user
    list_display = ('email','username','first_name','last_name','num','is_active','is_staff')
    fieldsets = (
        (None,{'fields': ('email','password')}),
        ('personal info',{'fields':('username','num','first_name','last_name')}),
        ('permissions',{'fields':('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
    )
    add_fieldsets = (
        (None,{
            'classes' : ('wide',),
            'fields' :('email', 'username','first_name','last_name','num','password1','password2' ,'is_staff', 'is_active'),
        }),
    )
    ordering = ('email',)
# Register your models here.
