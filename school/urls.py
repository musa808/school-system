from django.urls import path
from . import views

urlpatterns = [
    # Auth
    path('', views.dashboard, name='dashboard'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),

    # Students
    path('students/', views.student_list, name='student_list'),
    path('students/add/', views.student_add, name='student_add'),
    path('students/<int:pk>/', views.student_detail, name='student_detail'),
    path('students/<int:pk>/edit/', views.student_edit, name='student_edit'),
    path('students/<int:pk>/delete/', views.student_delete, name='student_delete'),
    path('register/', views.register_view, name='register'),
    # Staff
    path('staff/', views.staff_list, name='staff_list'),
    path('staff/add/', views.staff_add, name='staff_add'),
    path('staff/<int:pk>/', views.staff_detail, name='staff_detail'),
    path('staff/<int:pk>/edit/', views.staff_edit, name='staff_edit'),

    # Classes
    path('classes/', views.class_list, name='class_list'),
    path('classes/add/', views.class_add, name='class_add'),
    path('classes/<int:pk>/', views.class_detail, name='class_detail'),

    # Grades
    path('grades/', views.grade_list, name='grade_list'),
    path('grades/add/', views.grade_add, name='grade_add'),

    # Subjects
    path('subjects/', views.subject_list, name='subject_list'),
    path('subjects/add/', views.subject_add, name='subject_add'),
    path('subjects/<int:pk>/edit/', views.subject_edit, name='subject_edit'),

    # Attendance
    path('attendance/', views.attendance_list, name='attendance_list'),
    path('attendance/mark/', views.attendance_mark, name='attendance_mark'),
    path('attendance/report/', views.attendance_report, name='attendance_report'),

    # Exams & Results
    path('exams/', views.exam_list, name='exam_list'),
    path('exams/add/', views.exam_add, name='exam_add'),
    path('exams/<int:pk>/', views.exam_detail, name='exam_detail'),
    path('results/', views.result_list, name='result_list'),
    path('results/add/', views.result_add, name='result_add'),
    path('results/report/', views.result_report, name='result_report'),

    # Fees
    path('fees/', views.fee_list, name='fee_list'),
    path('fees/structure/', views.fee_structure_list, name='fee_structure_list'),
    path('fees/structure/add/', views.fee_structure_add, name='fee_structure_add'),
    path('fees/payment/add/', views.fee_payment_add, name='fee_payment_add'),
    path('fees/payment/<int:pk>/receipt/', views.fee_receipt, name='fee_receipt'),
    path('fees/report/', views.fee_report, name='fee_report'),

    # Timetable
    path('timetable/', views.timetable_list, name='timetable_list'),
    path('timetable/add/', views.timetable_add, name='timetable_add'),

    # Announcements
    path('announcements/', views.announcement_list, name='announcement_list'),
    path('announcements/add/', views.announcement_add, name='announcement_add'),
    path('announcements/<int:pk>/edit/', views.announcement_edit, name='announcement_edit'),
    path('announcements/<int:pk>/delete/', views.announcement_delete, name='announcement_delete'),

    # Events
    path('events/', views.event_list, name='event_list'),
    path('events/add/', views.event_add, name='event_add'),

    # Leave Requests
    path('leaves/', views.leave_list, name='leave_list'),
    path('leaves/add/', views.leave_add, name='leave_add'),
    path('leaves/<int:pk>/review/', views.leave_review, name='leave_review'),

    # Reports
    path('reports/', views.reports_dashboard, name='reports_dashboard'),
    path('reports/students/', views.report_students, name='report_students'),
    path('reports/finance/', views.report_finance, name='report_finance'),

    # Academic Years
    path('academic-years/', views.academic_year_list, name='academic_year_list'),
    path('academic-years/add/', views.academic_year_add, name='academic_year_add'),
]