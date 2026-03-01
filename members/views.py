from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, JsonResponse
from django.db.models import Q
from django.db import transaction
from datetime import date, datetime
import json

from .models import Member, Attendance ,AssignedHistory
from .forms import MemberForm
from .assign_workplace import assign_workplace


# =========================
# AUTH VIEWS
# =========================
def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            messages.success(request, "Logged in successfully")
            return redirect('member_list')
        else:
            messages.error(request, "Invalid username or password")
    return render(request, 'members/login.html')

def logout_view(request):
    logout(request)
    messages.info(request, "Logged out")
    return redirect('login')

# =========================
# HELPER FUNCTIONS
# =========================
def calculate_age(birth_date):
    if not birth_date:
        return None
    today = date.today()
    age = today.year - birth_date.year
    if (today.month, today.day) < (birth_date.month, birth_date.day):
        age -= 1
    return age

def calculate_service_years(joined_date):
    if not joined_date:
        return None
    today = date.today()
    years = today.year - joined_date.year
    if (today.month, today.day) < (joined_date.month, joined_date.day):
        years -= 1
    return max(0, years)

# =========================
# MEMBER FILTER LOGIC
# =========================
def _filter_members(request):
    qs = Member.objects.all()

    # General search
    q = request.GET.get('q')
    if q:
        qs = qs.filter(
            Q(fullname__icontains=q) |
            Q(etf_no__icontains=q) |
            Q(telephone__icontains=q) |
            Q(nic_no__icontains=q) |
            Q(workplace__icontains=q)
        )

    # Filters
    if request.GET.get('gender'):
        qs = qs.filter(gender__iexact=request.GET.get('gender'))
    if request.GET.get('province'):
        qs = qs.filter(province__iexact=request.GET.get('province'))
    if request.GET.get('status'):
        qs = qs.filter(status__iexact=request.GET.get('status'))

    # Security/Cleaning service filter
    position_category = request.GET.get('position_category')
    if position_category:
        qs = qs.filter(position_category__iexact=position_category)

    # ETF filters
    etf_range = request.GET.get('etf_range')
    etf_list = request.GET.get('etf_list')
    if etf_range:
        try:
            start, end = etf_range.split('-')
            qs = qs.filter(etf_no__gte=start.strip(), etf_no__lte=end.strip())
        except ValueError:
            pass
    if etf_list:
        etf_values = [x.strip() for x in etf_list.split(',') if x.strip()]
        qs = qs.filter(etf_no__in=etf_values)

    # Date joined filters
    if request.GET.get('date_joined_from'):
        qs = qs.filter(date_joined__gte=request.GET.get('date_joined_from'))
    if request.GET.get('date_joined_to'):
        qs = qs.filter(date_joined__lte=request.GET.get('date_joined_to'))

    # Age filtering
    age_filter = request.GET.get('age')
    age_range = request.GET.get('age_range')
    if age_filter or age_range:
        members_with_age = []
        for member in qs:
            calculated_age = calculate_age(member.date_of_birth)
            if calculated_age is not None:
                if age_filter:
                    try:
                        target_age = int(age_filter)
                        if calculated_age == target_age:
                            members_with_age.append(member.pk)
                    except ValueError:
                        pass
                if age_range:
                    try:
                        min_age, max_age = map(int, age_range.split('-'))
                        if min_age <= calculated_age <= max_age:
                            members_with_age.append(member.pk)
                    except ValueError:
                        pass
        qs = qs.filter(pk__in=members_with_age)

    # Service years filtering
    service_filter = request.GET.get('service_years')
    service_range = request.GET.get('service_range')
    if service_filter or service_range:
        members_with_service = []
        for member in qs:
            calculated_service = calculate_service_years(member.date_joined)
            if calculated_service is not None:
                if service_filter:
                    try:
                        target_service = int(service_filter)
                        if calculated_service == target_service:
                            members_with_service.append(member.pk)
                    except ValueError:
                        pass
                if service_range:
                    try:
                        min_service, max_service = map(int, service_range.split('-'))
                        if min_service <= calculated_service <= max_service:
                            members_with_service.append(member.pk)
                    except ValueError:
                        pass
        qs = qs.filter(pk__in=members_with_service)

    return qs

# =========================
# MEMBER CRUD VIEWS
# =========================
@login_required
def member_list(request):
    members = _filter_members(request)
    for member in members:
        member.calculated_age = calculate_age(member.date_of_birth)
        member.calculated_service_years = calculate_service_years(member.date_joined)
    return render(request, 'members/member_list.html', {
        'members': members,
        'query': request.GET
    })

@login_required
def member_create(request):
    if request.method == 'POST':
        form = MemberForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, "Member added successfully")
            return redirect('member_list')
    else:
        form = MemberForm()
    return render(request, 'members/member_form.html', {'form': form})

@login_required
def member_update(request, pk):
    member = get_object_or_404(Member, pk=pk)
    if request.method == 'POST':
        form = MemberForm(request.POST, request.FILES, instance=member)
        if form.is_valid():
            form.save()
            messages.success(request, "Member updated successfully")
            return redirect('member_list')
    else:
        form = MemberForm(instance=member)
    return render(request, 'members/member_form.html', {'form': form})

@login_required
def member_delete(request, pk):
    member = get_object_or_404(Member, pk=pk)
    if request.method == 'POST':
        member.delete()
        messages.success(request, "Member deleted")
        return redirect('member_list')
    return render(request, 'members/member_confirm_delete.html', {'member': member})

# =========================
# EXPORT VIEWS
# =========================
@login_required
def export_members_csv(request):
    import csv
    members = _filter_members(request)
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename=members.csv'
    writer = csv.writer(response)
    writer.writerow([
        'ETF No', 'Full Name', 'Gender', 'Position Category', 'Status', 'Age', 'Service Years'
    ])
    for m in members:
        writer.writerow([
            m.etf_no, m.fullname, m.gender, m.position_category, m.status,
            calculate_age(m.date_of_birth), calculate_service_years(m.date_joined)
        ])
    return response

@login_required
def export_members_xlsx(request):
    try:
        import openpyxl
    except ImportError:
        return HttpResponse("Install openpyxl", status=500)
    members = _filter_members(request)
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Members"
    ws.append(['ETF No', 'Full Name', 'Gender', 'Position Category', 'Status', 'Age', 'Service Years'])
    for m in members:
        ws.append([
            m.etf_no, m.fullname, m.gender, m.position_category, m.status,
            calculate_age(m.date_of_birth), calculate_service_years(m.date_joined)
        ])
    from io import BytesIO
    buffer = BytesIO()
    wb.save(buffer)
    buffer.seek(0)
    response = HttpResponse(buffer, content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename=members.xlsx'
    return response

@login_required
def export_members_pdf(request):
    try:
        from weasyprint import HTML
    except ImportError:
        return HttpResponse("Install WeasyPrint", status=500)
    members = _filter_members(request)
    for member in members:
        member.calculated_age = calculate_age(member.date_of_birth)
        member.calculated_service_years = calculate_service_years(member.date_joined)
    html_content = render(request, 'members/export_pdf.html', {'members': members}).content.decode()
    pdf = HTML(string=html_content).write_pdf()
    response = HttpResponse(pdf, content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename=members.pdf'
    return response

# =========================
# ATTENDANCE PAGE
# =========================
@login_required
def attendance_page(request):
    members = Member.objects.filter(status='Active').order_by('etf_no')

    for member in members:
        member.calculated_service_years = calculate_service_years(member.date_joined)

    current_month = datetime.now().strftime('%Y-%m')

    return render(request, 'members/attendance_page.html', {
        'members': members,
        'selected_month': current_month
    })


# =========================
# SAVE ATTENDANCE (AJAX)
# =========================
@login_required
def save_attendance(request):
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Invalid request method'})

    try:
        data = json.loads(request.body)
        attendance_month_str = data.get('month')
        attendance_data = data.get('attendance_data', [])

        if not attendance_month_str:
            return JsonResponse({'success': False, 'error': 'Month is required'})

        attendance_month = datetime.strptime(
            attendance_month_str, '%Y-%m'
        ).date().replace(day=1)

        saved_count = 0

        with transaction.atomic():
            for record in attendance_data:
                member_id = record.get('member_id')
                service_days = int(record.get('service_days', 0))
                comment = record.get('comment', '')
                leave_dates = record.get('leave_dates', '')

                try:
                    member = Member.objects.get(pk=member_id)

                    Attendance.objects.update_or_create(
                        member_id=member.pk,
                        attendance_month=attendance_month,
                        defaults={
                            'member_etf_no': member.etf_no,
                            'member_fullname': member.fullname,
                            'service_days': service_days,
                            'comment': comment,
                            'leave_dates': leave_dates
                        }
                    )

                    saved_count += 1

                except Member.DoesNotExist:
                    continue

        return JsonResponse({
            'success': True,
            'message': f'{saved_count} attendance records saved successfully'
        })

    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


# =========================
# EXPORT ATTENDANCE PDF WITH FILTERS
# =========================
@login_required
def export_attendance_pdf(request):
    try:
        from weasyprint import HTML
    except ImportError:
        return HttpResponse("Install WeasyPrint first: pip install weasyprint", status=500)

    month_str = request.GET.get('month')
    if not month_str:
        return HttpResponse("Month is required", status=400)

    attendance_month = datetime.strptime(month_str, '%Y-%m').date().replace(day=1)

    # Base queryset for active members
    members = Member.objects.filter(status='Active').order_by('etf_no')

    # ✅ Apply filters from request GET parameters
    search = request.GET.get('search', '').strip()
    province = request.GET.get('province', '').strip()
    branch = request.GET.get('branch', '').strip()
    gender = request.GET.get('gender', '').strip()
    position_category = request.GET.get('position_category', '').strip()  # ✅ NEW

    # ✅ Apply filters
    if search:
        members = members.filter(
            Q(fullname__icontains=search) |
            Q(etf_no__icontains=search) |
            Q(nic_no__icontains=search)
        )
    if province:
        members = members.filter(province__icontains=province)
    if branch:
        members = members.filter(branch_name__icontains=branch)
    if gender:
        members = members.filter(gender__icontains=gender)
    if position_category:  # ✅ NEW FILTER
        members = members.filter(position_category__icontains=position_category)

    # Fetch attendance records for the selected month
    attendance_records = {
        att.member_id: att
        for att in Attendance.objects.filter(attendance_month=attendance_month)
    }

    # Prepare data for PDF
    members_data = []
    for member in members:
        attendance = attendance_records.get(member.pk)
        members_data.append({
            'member': member,
            'service_days': attendance.service_days if attendance else 0,
            'leave_dates': attendance.get_leave_dates_list() if attendance else [],
            'comment': attendance.comment if attendance else ''
        })

    # Render HTML template
    html_content = render(request, 'members/attendance_pdf.html', {
        'members_data': members_data,
        'month': attendance_month.strftime('%B %Y'),
        'generated_date': datetime.now(),
        'filters_applied': {
            'search': search,
            'province': province,
            'branch': branch,
            'gender': gender,
            'position_category': position_category,
        }
    }).content.decode()

    # Generate PDF
    pdf = HTML(string=html_content).write_pdf()

    response = HttpResponse(pdf, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename=attendance_{month_str}.pdf'

    return response


@login_required
def assign_workplace(request, pk):
    member = get_object_or_404(Member, pk=pk)

    if request.method == 'POST':
        new_workplace = request.POST.get('workplace')

        if new_workplace:
            # Update member current workplace
            member.workplace = new_workplace
            member.save()

            # 🔥 ADD RECORD TO AssignedHistory TABLE
            AssignedHistory.objects.create(
                member=member,
                assigned_place=new_workplace
            )

            messages.success(request, f"Workplace updated for {member.fullname}")
            return redirect('member_list')

        else:
            messages.error(request, "Please enter a workplace.")

    return render(request, 'members/assign_workplace.html', {'member': member})


@login_required
def assigned_history_list(request):
    history = AssignedHistory.objects.select_related('member').order_by('-assigned_date')
    return render(request, 'members/assigned_history.html', {
        'history': history
    })