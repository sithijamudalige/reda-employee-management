from django.contrib import admin
from django.utils.html import format_html
from .models import Member, Attendance, AssignedHistory, Login

@admin.register(Member)
class MemberAdmin(admin.ModelAdmin):
    list_display = ('etf_no', 'fullname', 'nic_no', 'telephone', 'position_category', 'photo_thumbnail')
    search_fields = ('fullname', 'etf_no', 'nic_no')
    list_filter = ('gender', 'marital_status')

    # Custom method to show photo
    def photo_thumbnail(self, obj):
        if obj.picture:
            return format_html('<img src="{}" width="50" height="50" style="object-fit:cover; border-radius:5px;" />', obj.picture.url)
        return "-"
    photo_thumbnail.short_description = 'Picture'


@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = [
        'member_fullname', 
        'member_etf_no', 
        'attendance_month', 
        'service_days', 
        'formatted_leave_dates',
        'comment', 
        'updated_at'
    ]
    list_filter = ['attendance_month']
    search_fields = ['member_fullname', 'member_etf_no', 'comment']
    date_hierarchy = 'attendance_month'
    ordering = ['-attendance_month', 'member_etf_no']
    
    # ✅ FIXED: Custom method to format leave dates nicely
    def formatted_leave_dates(self, obj):
        """Display leave dates as a formatted, colored list"""
        leave_dates = obj.get_leave_dates_list()
        if leave_dates:
            # Join dates with line breaks for better readability
            dates_html = '<br>'.join(leave_dates)
            return format_html(
                '<span style="color: #d9534f; font-weight: bold;">{}</span>', 
                dates_html
            )
        # ✅ FIX: Return plain string instead of format_html with no args
        return "-"
    
    formatted_leave_dates.short_description = 'Leave Dates'
    formatted_leave_dates.admin_order_field = 'leave_dates'


admin.site.register(Login)
admin.site.register(AssignedHistory)