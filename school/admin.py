from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import (
    User, AcademicYear, Grade, Section, Subject, Student,
    Attendance, Exam, Result, FeeStructure, FeePayment,
    Announcement, Timetable, Event, LeaveRequest
)


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ['username', 'first_name', 'last_name', 'email', 'role', 'is_active']
    list_filter = ['role', 'is_active']
    fieldsets = BaseUserAdmin.fieldsets + (
        ('School Info', {'fields': ('role', 'phone', 'address', 'photo')}),
    )
    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        ('School Info', {'fields': ('role', 'phone', 'address')}),
    )


@admin.register(AcademicYear)
class AcademicYearAdmin(admin.ModelAdmin):
    list_display = ['name', 'start_date', 'end_date', 'is_current']
    list_editable = ['is_current']


@admin.register(Grade)
class GradeAdmin(admin.ModelAdmin):
    list_display = ['name', 'description']


@admin.register(Section)
class SectionAdmin(admin.ModelAdmin):
    list_display = ['__str__', 'grade', 'class_teacher', 'academic_year', 'capacity']
    list_filter = ['grade', 'academic_year']


@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ['name', 'code', 'grade', 'teacher']
    list_filter = ['grade']
    search_fields = ['name', 'code']


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ['get_full_name', 'student_id', 'section', 'gender', 'is_active', 'admission_date']
    list_filter = ['section__grade', 'gender', 'is_active']
    search_fields = ['first_name', 'last_name', 'student_id']
    list_editable = ['is_active']


@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = ['student', 'date', 'status', 'section', 'marked_by']
    list_filter = ['status', 'date', 'section']
    date_hierarchy = 'date'


@admin.register(Exam)
class ExamAdmin(admin.ModelAdmin):
    list_display = ['name', 'exam_type', 'subject', 'section', 'date', 'total_marks']
    list_filter = ['exam_type', 'subject__grade']
    date_hierarchy = 'date'


@admin.register(Result)
class ResultAdmin(admin.ModelAdmin):
    list_display = ['student', 'exam', 'marks_obtained', 'grade_letter']
    list_filter = ['exam__subject__grade']
    search_fields = ['student__first_name', 'student__last_name']


@admin.register(FeeStructure)
class FeeStructureAdmin(admin.ModelAdmin):
    list_display = ['name', 'fee_type', 'grade', 'amount', 'academic_year']
    list_filter = ['fee_type', 'grade', 'academic_year']


@admin.register(FeePayment)
class FeePaymentAdmin(admin.ModelAdmin):
    list_display = ['student', 'fee_structure', 'amount_due', 'amount_paid', 'status', 'due_date', 'receipt_number']
    list_filter = ['status']
    search_fields = ['student__first_name', 'student__last_name', 'receipt_number']
    date_hierarchy = 'due_date'


@admin.register(Announcement)
class AnnouncementAdmin(admin.ModelAdmin):
    list_display = ['title', 'audience', 'created_by', 'created_at', 'is_active']
    list_filter = ['audience', 'is_active']
    list_editable = ['is_active']


@admin.register(Timetable)
class TimetableAdmin(admin.ModelAdmin):
    list_display = ['section', 'subject', 'teacher', 'day', 'start_time', 'end_time']
    list_filter = ['day', 'section__grade']


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ['title', 'date', 'end_date', 'location', 'created_by']
    date_hierarchy = 'date'


@admin.register(LeaveRequest)
class LeaveRequestAdmin(admin.ModelAdmin):
    list_display = ['__str__', 'leave_type', 'start_date', 'end_date', 'status', 'reviewed_by']
    list_filter = ['status', 'leave_type']
    list_editable = ['status']