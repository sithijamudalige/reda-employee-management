from django.db import models


# ----------------------------
# District Model
# ----------------------------
class District(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name


# ----------------------------
# Divisional Secretariat (DS)
# ----------------------------
class DSDivision(models.Model):
    name = models.CharField(max_length=150)
    district = models.ForeignKey(
        District,
        on_delete=models.CASCADE,
        related_name='ds_divisions'
    )

    def __str__(self):
        return f"{self.name} ({self.district.name})"


# ----------------------------
# Police Station
# ----------------------------
class PoliceStation(models.Model):
    station_name = models.CharField(max_length=150)
    division = models.CharField(max_length=150)
    oic_mobile = models.CharField(max_length=20, blank=True, null=True)
    office_phone = models.CharField(max_length=20, blank=True, null=True)

    def __str__(self):
        return self.station_name


# ----------------------------
# Member Model
# ----------------------------
from django.db import models
from datetime import date

class Member(models.Model):

    GENDER_CHOICES = [
        ('Male', 'Male'),
        ('Female', 'Female'),
        ('Other', 'Other'),
    ]

    MARITAL_STATUS_CHOICES = [
        ('Single', 'Single'),
        ('Married', 'Married'),
        ('Divorced', 'Divorced'),
        ('Widowed', 'Widowed'),
    ]

    STATUS_CHOICES = [
        ('Active', 'Active'),
        ('Inactive', 'Inactive'),
    ]

    POSITION_CATEGORY_CHOICES = [
        ('Security', 'Security'),
        ('Cleaning', 'Cleaning'),
    ]

    # 🔹 NEW: Veteran / Non-Veteran field
    VETERAN_STATUS_CHOICES = [
        ('Veteran', 'Veteran'),
        ('Non-Veteran', 'Non-Veteran'),
    ]

    etf_no = models.CharField(max_length=50, unique=True)
    fullname = models.CharField(max_length=255)
    gender = models.CharField(max_length=20, choices=GENDER_CHOICES)
    nationality = models.CharField(max_length=100)
    nic_no = models.CharField(max_length=20)
    date_of_birth = models.DateField(blank=True, null=True)
    address = models.TextField()
    workplace = models.CharField(max_length=255)

    # 🔹 Bank details
    bank_name = models.CharField(max_length=150, blank=True, null=True)
    salary_bank_branch_no = models.CharField(max_length=100)
    branch_name = models.CharField(max_length=255, blank=True, null=True)

    province = models.CharField(max_length=100, blank=True, null=True)
    provincial_council = models.CharField(max_length=150, blank=True, null=True)
    acc_no = models.CharField(max_length=50)
    telephone = models.CharField(max_length=20)
    picture = models.ImageField(upload_to='members/', blank=True, null=True)
    date_joined = models.DateField(blank=True, null=True)
    date_resigned = models.DateField(blank=True, null=True)

    # 🔹 LOCATION FIELDS
    district = models.ForeignKey(
        'District',
        on_delete=models.SET_NULL,
        blank=True,
        null=True
    )
    ds_division = models.ForeignKey(
        'DSDivision',
        on_delete=models.SET_NULL,
        blank=True,
        null=True
    )
    police_station = models.ForeignKey(
        'PoliceStation',
        on_delete=models.SET_NULL,
        blank=True,
        null=True
    )

    marital_status = models.CharField(max_length=20, choices=MARITAL_STATUS_CHOICES)
    spouse_name = models.CharField(max_length=255, blank=True, null=True)
    no_of_children = models.IntegerField(default=0)
    education_qualifications = models.TextField()
    experience = models.TextField()
    position_category = models.CharField(max_length=100, choices=POSITION_CATEGORY_CHOICES)

    # 🔹 Veteran / Non-Veteran
    veteran_status = models.CharField(
        max_length=20,
        choices=VETERAN_STATUS_CHOICES,
        default='Non-Veteran'
    )

    # 🔹 NEW: Status field (defaults to Active)
    status = models.CharField(
        max_length=10, 
        choices=STATUS_CHOICES, 
        default='Active'
    )

    def __str__(self):
        return f"{self.etf_no} - {self.fullname}"

    @property
    def age(self):
        """Calculate age from date_of_birth and today's date."""
        if self.date_of_birth:
            today = date.today()
            return (
                today.year
                - self.date_of_birth.year
                - ((today.month, today.day) < (self.date_of_birth.month, self.date_of_birth.day))
            )
        return None
# ----------------------------
# Custom Login Model (⚠️ Demo only)
# ----------------------------
class Login(models.Model):
    username = models.CharField(max_length=150, unique=True)
    password = models.CharField(max_length=255)  # ⚠️ Plain text, not secure

    def __str__(self):
        return self.username
    
from django.db import models

class Attendance(models.Model):
    """Model to store monthly attendance records in Access database"""
    member_id = models.IntegerField(default=0)  # Store member ID instead of ForeignKey
    member_etf_no = models.CharField(max_length=50, default='')  # For easier lookup
    member_fullname = models.CharField(max_length=255, default='')
    attendance_month = models.DateField()  # First day of the month (e.g., 2026-01-01)
    service_days = models.IntegerField(default=0)
    leave_dates = models.TextField(blank=True, null=True)  # Store leave dates as CSV string e.g., "2026-02-01,2026-02-05"
    comment = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'attendance'  # Table name in Access database
        unique_together = ['member_id', 'attendance_month']
        ordering = ['-attendance_month', 'member_etf_no']
        verbose_name = 'Attendance Record'
        verbose_name_plural = 'Attendance Records'
    
    def __str__(self):
        return f"{self.member_fullname} - {self.attendance_month.strftime('%B %Y')}"
    
    def get_leave_dates_list(self):
        """Return leave dates as a Python list"""
        if self.leave_dates:
            return [date.strip() for date in self.leave_dates.split(',') if date.strip()]
        return []
class AssignedHistory(models.Model):
    member = models.ForeignKey('Member', on_delete=models.CASCADE, related_name='assign_history')
    assigned_place = models.CharField(max_length=255)
    assigned_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.member.fullname} - {self.assigned_place}"