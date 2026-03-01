from django.urls import path
from . import views

urlpatterns = [
    # Authentication
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),

    # Member CRUD
    path('', views.member_list, name='member_list'),
    path('create/', views.member_create, name='member_create'),
    path('<int:pk>/update/', views.member_update, name='member_update'),
    path('<int:pk>/delete/', views.member_delete, name='member_delete'),
    
     path('attendance/', views.attendance_page, name='attendance_page'),
    path('attendance/save/', views.save_attendance, name='save_attendance'),
    path('attendance/export-pdf/', views.export_attendance_pdf, name='export_attendance_pdf'),

    # Export endpoints
    path('export/csv/', views.export_members_csv, name='export_members_csv'),
    path('export/xlsx/', views.export_members_xlsx, name='export_members_xlsx'),
    path('export/pdf/', views.export_members_pdf, name='export_members_pdf'),
    path('members/<int:pk>/assign-workplace/', views.assign_workplace, name='assign_workplace'),
    path('assigned-history/', views.assigned_history_list, name='assigned_history'),
]