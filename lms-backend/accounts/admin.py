from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.html import format_html
from .models import CustomUser, Profile


class ProfileInline(admin.StackedInline):
    """
    Inline editing for Profile directly within CustomUser admin.
    """
    model = Profile
    can_delete = False
    verbose_name_plural = "Profile"
    fk_name = "user"
    extra = 0


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    """
    Custom admin configuration for CustomUser.
    Uses email as the primary identifier and includes role management.
    """
    inlines = [ProfileInline]

    list_display = ("id", "email", "username", "role", "is_staff", "is_active", "date_joined")
    list_filter = ("role", "is_staff", "is_active", "is_superuser")
    search_fields = ("email", "username", "role")
    ordering = ("email",)

    fieldsets = (
        (None, {"fields": ("email", "password")}),
        ("Personal info", {"fields": ("username", "role")}),
        ("Permissions", {"fields": ("is_active", "is_staff", "is_superuser", "groups", "user_permissions")}),
        ("Important dates", {"fields": ("last_login", "date_joined", "updated_at")}),
    )

    add_fieldsets = (
        (None, {
            "classes": ("wide",),
            "fields": ("email", "username", "role", "password1", "password2", "is_staff", "is_active"),
        }),
    )

    readonly_fields = ("date_joined", "updated_at")


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    """
    Admin configuration for Profile model.
    """
    list_display = ("user", "bio", "location", "birth_date", "avatar_preview")
    search_fields = ("user__email", "user__username", "location")
    list_filter = ("birth_date", "location")

    def avatar_preview(self, obj):
        """
        Show avatar thumbnail in admin list view.
        """
        if obj.avatar:
            return format_html('<img src="{}" style="width:40px; height:40px; border-radius:50%;" />', obj.avatar.url)
        return "—"
    avatar_preview.short_description = "Avatar"
