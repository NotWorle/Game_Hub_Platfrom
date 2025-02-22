from django.contrib import admin
from .models import CustomUser
from django.contrib.auth.admin import UserAdmin

class RoleRequestAdmin(admin.ModelAdmin):
    list_display = ['username', 'email', 'date_joined', 'role', 'requested_role', 'request_status']
    search_fields = ['username', 'email', 'role']
    list_filter = ['request_status', 'role']
    actions = ['approve_request', 'reject_request']

    @admin.action(description="Approve selected requests")
    def approve_request(self, request, queryset):
        approved_count = 0
        for user in queryset.filter(request_status='pending'):
            if user.requested_role and user.requested_role in [CustomUser.ROLE_DEVELOPER, CustomUser.ROLE_DESIGNER, CustomUser.ROLE_DEV_DES]:
                user.role = user.requested_role
                user.request_status = 'approved'
                user.requested_role = None
                user.save()
                approved_count += 1
        self.message_user(request, f"{approved_count} request(s) have been approved.")

    @admin.action(description="Reject selected requests")
    def reject_request(self, request, queryset):
        rejected_count = 0
        for user in queryset.filter(request_status='pending'):
            user.request_status = 'rejected'
            user.requested_role = None
            user.save()
            rejected_count += 1
        self.message_user(request, f"{rejected_count} request(s) have been rejected.")

# Đăng ký `CustomUser` với `RoleRequestAdmin` trong Django Admin
admin.site.register(CustomUser, RoleRequestAdmin)
