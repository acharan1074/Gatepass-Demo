from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.db import transaction
from django.contrib import messages
from .models import User, Student, Warden, Security, GatePass, ParentVerification, Notification


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    """Custom User Admin"""
    
    list_display = ('username', 'email', 'role', 'gender', 'is_approved', 'is_active', 'date_joined')
    list_filter = ('role', 'gender', 'is_approved', 'is_active', 'is_staff')
    search_fields = ('username', 'email', 'first_name', 'last_name')
    ordering = ('-date_joined',)
    
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'email', 'mobile_number', 'gender')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Gatepass Info', {'fields': ('role', 'is_approved')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'password1', 'password2', 'role', 'is_approved'),
        }),
    )


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    """Student Admin"""
    
    list_display = ('student_name', 'hall_ticket_no', 'room_no', 'parent_name', 'parent_mobile', 'user')
    list_filter = ('user__gender', 'user__is_approved')
    search_fields = ('student_name', 'hall_ticket_no', 'parent_name', 'parent_mobile')
    readonly_fields = ('username_format',)


@admin.register(Warden)
class WardenAdmin(admin.ModelAdmin):
    """Warden Admin"""
    
    list_display = ('name', 'department', 'user')
    search_fields = ('name', 'department')


@admin.register(Security)
class SecurityAdmin(admin.ModelAdmin):
    """Security Admin"""
    
    list_display = ('name', 'shift', 'user')
    search_fields = ('name', 'shift')


@admin.register(GatePass)
class GatePassAdmin(admin.ModelAdmin):
    """GatePass Admin"""
    
    list_display = ('student', 'outing_date', 'outing_time', 'status', 'created_at')
    list_filter = ('status', 'outing_date', 'student__user__gender')
    search_fields = ('student__student_name', 'student__hall_ticket_no')
    readonly_fields = ('created_at', 'updated_at')
    actions = ['delete_selected_safe']
    list_per_page = 50  # Limit items per page to avoid field limit issues
    list_max_show_all = 100  # Maximum number of items to show when "Show all" is clicked
    show_full_result_count = False  # Don't count all items (performance)
    
    fieldsets = (
        ('Student Information', {
            'fields': ('student',)
        }),
        ('Outing Details', {
            'fields': ('outing_date', 'outing_time', 'expected_return_date', 'expected_return_time', 'purpose')
        }),
        ('Approval Status', {
            'fields': ('status', 'warden_approval', 'security_approval', 'warden_rejection_reason', 'parent_verification')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def delete_selected_safe(self, request, queryset):
        """Custom delete action that handles large querysets without hitting field limits"""
        count = queryset.count()
        if count == 0:
            self.message_user(request, 'No records selected.', messages.WARNING)
            return
        
        try:
            with transaction.atomic():
                # Delete related notifications first
                Notification.objects.filter(gatepass__in=queryset).delete()
                # Delete related parent verifications
                ParentVerification.objects.filter(gatepass__in=queryset).delete()
                # Finally delete gatepasses
                deleted_count, _ = queryset.delete()
                
            self.message_user(
                request,
                f'Successfully deleted {deleted_count} gatepass record(s) and related data.',
                messages.SUCCESS
            )
        except Exception as e:
            self.message_user(
                request,
                f'Error deleting records: {str(e)}',
                messages.ERROR
            )
    
    delete_selected_safe.short_description = "Delete selected gatepasses (handles large selections)"


@admin.register(ParentVerification)
class ParentVerificationAdmin(admin.ModelAdmin):
    """Parent Verification Admin"""
    
    list_display = ('gatepass', 'parent_mobile', 'is_verified', 'verified_at', 'created_at')
    list_filter = ('is_verified', 'created_at')
    search_fields = ('gatepass__student__student_name', 'parent_mobile')


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    """Notification Admin"""
    
    list_display = ('user', 'gatepass', 'notification_type', 'is_read', 'created_at')
    list_filter = ('notification_type', 'is_read', 'created_at')
    search_fields = ('user__username', 'message')
    readonly_fields = ('created_at',)