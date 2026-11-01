from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import User


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    model = User

    list_display = (
        "username",
        "email",
        "first_name",
        "last_name",
        "role",
        "email_verified",
        "is_staff",
    )

    list_filter = (
        "role",
        "email_verified",
        "is_staff",
        "is_active",
    )

    search_fields = (
        "username",
        "email",
        "first_name",
        "last_name",
    )

    fieldsets = UserAdmin.fieldsets + (
        (
            "اطلاعات سامانه آموزشی",
            {
                "fields": (
                    "role",
                    "phone",
                    "email_verified",
                )
            },
        ),
    )

    add_fieldsets = UserAdmin.add_fieldsets + (
        (
            "اطلاعات سامانه آموزشی",
            {
                "fields": (
                    "email",
                    "role",
                    "phone",
                )
            },
        ),
    )