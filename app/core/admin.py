"""Django admin customization"""

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _

from core.models import User, Recipe, Tag


class UserAdmin(BaseUserAdmin):
    """Define the admin pages for users."""

    # Edit List user page
    ordering = ['id']
    list_display = ['email', 'name']

    # Edit detail view user page
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        (
            _('Permissions'),
            {
                'fields': (
                    'is_active',
                    'is_staff',
                    'is_superuser',
                )
            }
        ),
        (_('Important dates'), {'fields': ('last_login',)}),
    )
    readonly_fields = ['last_login']

    # Edit add user page
    add_fieldsets = (
        (None, {
            # classes ir realted to CSS configuration.
            'classes': ('wide',),
            'fields': (
                'email',
                'password1',
                'password2',
                'name',
                'is_staff',
                'is_superuser',
            )
        }),
    )


# Register your models here.
admin.site.register(User, UserAdmin)
admin.site.register(Recipe)
admin.site.register(Tag)
