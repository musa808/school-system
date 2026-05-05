from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Count, Sum, Q, Avg
from django.utils import timezone
from django.http import JsonResponse
import uuid
from datetime import date, timedelta

from .models import *
from .forms import *


# ─── AUTH ────────────────────────────────────────────────────────────────────

def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    form = LoginForm(request, data=request.POST or None)
    if request.method == 'POST' and form.is_valid():
        user = form.get_user()
        login(request, user)
        messages.success(request, f'Welcome back, {user.get_full_name() or user.username}!')
        return redirect('dashboard')
    return render(request, 'school/login.html', {'form': form})


@login_required
def logout_view(request):
    logout(request)
    return redirect('login')


# ─── DASHBOARD ───────────────────────────────────────────────────────────────

@login_required
def dashboard(request):
    today = date.today()
    stats = {
        'total_students': Student.objects.filter(is_active=True).count(),
        'total_staff': User.objects.filter(role__in=['teacher','admin','accountant','principal']).count(),
        'total_sections': Section.objects.count(),
        'pending_fees': FeePayment.objects.filter(status__in=['pending','overdue']).count(),
    }
    recent_announcements = Announcement.objects.filter(is_active=True)[:5]
    upcoming_events = Event.objects.filter(date__gte=today).order_by('date')[:5]
    recent_students = Student.objects.filter(is_active=True).order_by('-admission_date')[:5]
    today_attendance = Attendance.objects.filter(date=today)
    present_today = today_attendance.filter(status='present').count()
    absent_today = today_attendance.filter(status='absent').count()

    context = {
        'stats': stats,
        'recent_announcements': recent_announcements,
        'upcoming_events': upcoming_events,
        'recent_students': recent_students,
        'present_today': present_today,
        'absent_today': absent_today,
        'today': today,
    }
    return render(request, 'school/dashboard.html', context)


# ─── STUDENTS ────────────────────────────────────────────────────────────────

@login_required
def student_list(request):
    q = request.GET.get('q', '')
    section_id = request.GET.get('section', '')
    students = Student.objects.filter(is_active=True).select_related('section__grade')
    if q:
        students = students.filter(Q(first_name__icontains=q) | Q(last_name__icontains=q) | Q(student_id__icontains=q))
    if section_id:
        students = students.filter(section_id=section_id)
    sections = Section.objects.select_related('grade').all()
    return render(request, 'school/student_list.html', {'students': students, 'sections': sections, 'q': q, 'selected_section': section_id})


@login_required
def student_detail(request, pk):
    student = get_object_or_404(Student, pk=pk)
    attendances = student.attendances.order_by('-date')[:30]
    results = student.results.select_related('exam__subject').order_by('-exam__date')[:20]
    payments = student.payments.select_related('fee_structure').order_by('-due_date')[:10]
    leave_requests = student.leave_requests.order_by('-start_date')[:10]

    present_count = student.attendances.filter(status='present').count()
    total_attendance = student.attendances.count()
    attendance_pct = round((present_count / total_attendance * 100), 1) if total_attendance else 0

    context = {
        'student': student,
        'attendances': attendances,
        'results': results,
        'payments': payments,
        'leave_requests': leave_requests,
        'attendance_pct': attendance_pct,
        'present_count': present_count,
        'total_attendance': total_attendance,
    }
    return render(request, 'school/student_detail.html', context)


@login_required
def student_add(request):
    form = StudentForm(request.POST or None, request.FILES or None)
    if form.is_valid():
        student = form.save(commit=False)
        if not student.student_id:
            student.student_id = f"STU{str(uuid.uuid4().int)[:6].upper()}"
        student.save()
        messages.success(request, 'Student added successfully.')
        return redirect('student_list')
    return render(request, 'school/student_form.html', {'form': form, 'title': 'Add Student'})


@login_required
def student_edit(request, pk):
    student = get_object_or_404(Student, pk=pk)
    form = StudentForm(request.POST or None, request.FILES or None, instance=student)
    if form.is_valid():
        form.save()
        messages.success(request, 'Student updated successfully.')
        return redirect('student_detail', pk=pk)
    return render(request, 'school/student_form.html', {'form': form, 'title': 'Edit Student', 'student': student})


@login_required
def student_delete(request, pk):
    student = get_object_or_404(Student, pk=pk)
    if request.method == 'POST':
        student.is_active = False
        student.save()
        messages.success(request, 'Student removed successfully.')
        return redirect('student_list')
    return render(request, 'school/confirm_delete.html', {'object': student, 'name': student.get_full_name()})


# ─── STAFF ───────────────────────────────────────────────────────────────────

@login_required
def staff_list(request):
    q = request.GET.get('q', '')
    role = request.GET.get('role', '')
    staff = User.objects.filter(role__in=['teacher','accountant','principal','admin'])
    if q:
        staff = staff.filter(Q(first_name__icontains=q) | Q(last_name__icontains=q) | Q(username__icontains=q))
    if role:
        staff = staff.filter(role=role)
    return render(request, 'school/staff_list.html', {'staff': staff, 'q': q, 'selected_role': role})


@login_required
def staff_add(request):
    form = UserForm(request.POST or None, request.FILES or None)
    if form.is_valid():
        form.save()
        messages.success(request, 'Staff member added successfully.')
        return redirect('staff_list')
    return render(request, 'school/staff_form.html', {'form': form, 'title': 'Add Staff Member'})


@login_required
def staff_detail(request, pk):
    staff = get_object_or_404(User, pk=pk)
    sections = staff.class_sections.select_related('grade').all()
    subjects = staff.subjects.select_related('grade').all()
    return render(request, 'school/staff_detail.html', {'staff': staff, 'sections': sections, 'subjects': subjects})


@login_required
def staff_edit(request, pk):
    staff = get_object_or_404(User, pk=pk)
    form = UserForm(request.POST or None, request.FILES or None, instance=staff)
    if form.is_valid():
        form.save()
        messages.success(request, 'Staff updated successfully.')
        return redirect('staff_detail', pk=pk)
    return render(request, 'school/staff_form.html', {'form': form, 'title': 'Edit Staff', 'staff': staff})


# ─── GRADES & CLASSES ────────────────────────────────────────────────────────

@login_required
def grade_list(request):
    grades = Grade.objects.annotate(subject_count=Count('subjects'), section_count=Count('sections'))
    return render(request, 'school/grade_list.html', {'grades': grades})


@login_required
def grade_add(request):
    form = GradeForm(request.POST or None)
    if form.is_valid():
        form.save()
        messages.success(request, 'Grade added.')
        return redirect('grade_list')
    return render(request, 'school/simple_form.html', {'form': form, 'title': 'Add Grade', 'back_url': 'grade_list'})


@login_required
def class_list(request):
    sections = Section.objects.select_related('grade', 'class_teacher', 'academic_year').annotate(student_count=Count('students'))
    return render(request, 'school/class_list.html', {'sections': sections})


@login_required
def class_add(request):
    form = SectionForm(request.POST or None)
    if form.is_valid():
        form.save()
        messages.success(request, 'Class section added.')
        return redirect('class_list')
    return render(request, 'school/simple_form.html', {'form': form, 'title': 'Add Class Section', 'back_url': 'class_list'})


@login_required
def class_detail(request, pk):
    section = get_object_or_404(Section, pk=pk)
    students = section.students.filter(is_active=True)
    timetables = section.timetables.select_related('subject', 'teacher').order_by('day', 'start_time')
    today = date.today()
    today_attendance = Attendance.objects.filter(section=section, date=today)
    return render(request, 'school/class_detail.html', {
        'section': section, 'students': students,
        'timetables': timetables, 'today_attendance': today_attendance,
    })


# ─── SUBJECTS ────────────────────────────────────────────────────────────────

@login_required
def subject_list(request):
    subjects = Subject.objects.select_related('grade', 'teacher').all()
    return render(request, 'school/subject_list.html', {'subjects': subjects})


@login_required
def subject_add(request):
    form = SubjectForm(request.POST or None)
    if form.is_valid():
        form.save()
        messages.success(request, 'Subject added.')
        return redirect('subject_list')
    return render(request, 'school/simple_form.html', {'form': form, 'title': 'Add Subject', 'back_url': 'subject_list'})


@login_required
def subject_edit(request, pk):
    subject = get_object_or_404(Subject, pk=pk)
    form = SubjectForm(request.POST or None, instance=subject)
    if form.is_valid():
        form.save()
        messages.success(request, 'Subject updated.')
        return redirect('subject_list')
    return render(request, 'school/simple_form.html', {'form': form, 'title': 'Edit Subject', 'back_url': 'subject_list'})


# ─── ATTENDANCE ───────────────────────────────────────────────────────────────

@login_required
def attendance_list(request):
    date_filter = request.GET.get('date', str(date.today()))
    section_id = request.GET.get('section', '')
    attendances = Attendance.objects.select_related('student', 'section__grade').filter(date=date_filter)
    if section_id:
        attendances = attendances.filter(section_id=section_id)
    sections = Section.objects.select_related('grade').all()
    stats = {
        'present': attendances.filter(status='present').count(),
        'absent': attendances.filter(status='absent').count(),
        'late': attendances.filter(status='late').count(),
    }
    return render(request, 'school/attendance_list.html', {
        'attendances': attendances, 'sections': sections,
        'date_filter': date_filter, 'selected_section': section_id, 'stats': stats
    })


@login_required
def attendance_mark(request):
    section_id = request.GET.get('section', '')
    date_str = request.GET.get('date', str(date.today()))
    sections = Section.objects.select_related('grade').all()
    students = []
    if section_id:
        section = get_object_or_404(Section, pk=section_id)
        students = section.students.filter(is_active=True)
        existing = {a.student_id: a for a in Attendance.objects.filter(section=section, date=date_str)}
        if request.method == 'POST':
            for student in students:
                status = request.POST.get(f'status_{student.id}', 'absent')
                remarks = request.POST.get(f'remarks_{student.id}', '')
                obj, created = Attendance.objects.update_or_create(
                    student=student, date=date_str,
                    defaults={'status': status, 'section': section, 'remarks': remarks, 'marked_by': request.user}
                )
            messages.success(request, 'Attendance marked successfully.')
            return redirect('attendance_list')
        students_with_status = [(s, existing.get(s.id)) for s in students]
        return render(request, 'school/attendance_mark.html', {
            'section': section, 'students_with_status': students_with_status,
            'date_str': date_str, 'sections': sections, 'selected_section': section_id
        })
    return render(request, 'school/attendance_mark.html', {'sections': sections, 'date_str': date_str})


@login_required
def attendance_report(request):
    section_id = request.GET.get('section', '')
    month = request.GET.get('month', str(date.today().month))
    year = request.GET.get('year', str(date.today().year))
    sections = Section.objects.select_related('grade').all()
    report_data = []
    if section_id:
        section = get_object_or_404(Section, pk=section_id)
        students = section.students.filter(is_active=True)
        for student in students:
            att = student.attendances.filter(date__month=month, date__year=year)
            present = att.filter(status='present').count()
            total = att.count()
            report_data.append({
                'student': student,
                'present': present,
                'absent': att.filter(status='absent').count(),
                'late': att.filter(status='late').count(),
                'total': total,
                'pct': round(present / total * 100, 1) if total else 0
            })
    return render(request, 'school/attendance_report.html', {
        'sections': sections, 'report_data': report_data,
        'selected_section': section_id, 'month': month, 'year': year
    })


# ─── EXAMS & RESULTS ─────────────────────────────────────────────────────────

@login_required
def exam_list(request):
    exams = Exam.objects.select_related('subject__grade', 'section').order_by('-date')
    return render(request, 'school/exam_list.html', {'exams': exams})


@login_required
def exam_add(request):
    form = ExamForm(request.POST or None)
    if form.is_valid():
        form.save()
        messages.success(request, 'Exam added.')
        return redirect('exam_list')
    return render(request, 'school/simple_form.html', {'form': form, 'title': 'Add Exam', 'back_url': 'exam_list'})


@login_required
def exam_detail(request, pk):
    exam = get_object_or_404(Exam, pk=pk)
    results = exam.results.select_related('student').order_by('-marks_obtained')
    avg_marks = results.aggregate(avg=Avg('marks_obtained'))['avg'] or 0
    pass_count = results.filter(marks_obtained__gte=exam.passing_marks).count()
    return render(request, 'school/exam_detail.html', {
        'exam': exam, 'results': results,
        'avg_marks': round(avg_marks, 2), 'pass_count': pass_count,
        'total_students': results.count()
    })


@login_required
def result_list(request):
    results = Result.objects.select_related('student', 'exam__subject').order_by('-exam__date')[:100]
    return render(request, 'school/result_list.html', {'results': results})


@login_required
def result_add(request):
    form = ResultForm(request.POST or None)
    if form.is_valid():
        form.save()
        messages.success(request, 'Result recorded.')
        return redirect('result_list')
    return render(request, 'school/simple_form.html', {'form': form, 'title': 'Add Result', 'back_url': 'result_list'})


@login_required
def result_report(request):
    student_id = request.GET.get('student', '')
    student = None
    results = []
    if student_id:
        student = get_object_or_404(Student, pk=student_id)
        results = student.results.select_related('exam__subject').order_by('-exam__date')
    students = Student.objects.filter(is_active=True)
    return render(request, 'school/result_report.html', {
        'students': students, 'student': student, 'results': results
    })


# ─── FEES ────────────────────────────────────────────────────────────────────

@login_required
def fee_list(request):
    payments = FeePayment.objects.select_related('student', 'fee_structure').order_by('-due_date')
    status_filter = request.GET.get('status', '')
    if status_filter:
        payments = payments.filter(status=status_filter)
    total_collected = payments.filter(status='paid').aggregate(t=Sum('amount_paid'))['t'] or 0
    total_pending = payments.filter(status__in=['pending','overdue']).aggregate(t=Sum('amount_due'))['t'] or 0
    return render(request, 'school/fee_list.html', {
        'payments': payments, 'total_collected': total_collected,
        'total_pending': total_pending, 'status_filter': status_filter
    })


@login_required
def fee_structure_list(request):
    structures = FeeStructure.objects.select_related('grade', 'academic_year').all()
    return render(request, 'school/fee_structure_list.html', {'structures': structures})


@login_required
def fee_structure_add(request):
    form = FeeStructureForm(request.POST or None)
    if form.is_valid():
        form.save()
        messages.success(request, 'Fee structure added.')
        return redirect('fee_structure_list')
    return render(request, 'school/simple_form.html', {'form': form, 'title': 'Add Fee Structure', 'back_url': 'fee_structure_list'})


@login_required
def fee_payment_add(request):
    form = FeePaymentForm(request.POST or None)
    if form.is_valid():
        payment = form.save(commit=False)
        payment.recorded_by = request.user
        payment.receipt_number = f"RCP{str(uuid.uuid4().int)[:8].upper()}"
        if payment.amount_paid >= payment.amount_due:
            payment.status = 'paid'
        elif payment.amount_paid > 0:
            payment.status = 'partial'
        elif payment.due_date < date.today():
            payment.status = 'overdue'
        payment.save()
        messages.success(request, f'Payment recorded. Receipt: {payment.receipt_number}')
        return redirect('fee_receipt', pk=payment.pk)
    return render(request, 'school/simple_form.html', {'form': form, 'title': 'Record Payment', 'back_url': 'fee_list'})


@login_required
def fee_receipt(request, pk):
    payment = get_object_or_404(FeePayment, pk=pk)
    return render(request, 'school/fee_receipt.html', {'payment': payment})


@login_required
def fee_report(request):
    grade_id = request.GET.get('grade', '')
    grades = Grade.objects.all()
    data = []
    if grade_id:
        grade = get_object_or_404(Grade, pk=grade_id)
        students = Student.objects.filter(section__grade=grade, is_active=True)
        for student in students:
            paid = student.payments.filter(status='paid').aggregate(t=Sum('amount_paid'))['t'] or 0
            pending = student.payments.filter(status__in=['pending','overdue']).aggregate(t=Sum('amount_due'))['t'] or 0
            data.append({'student': student, 'paid': paid, 'pending': pending})
    return render(request, 'school/fee_report.html', {'grades': grades, 'data': data, 'selected_grade': grade_id})


# ─── TIMETABLE ───────────────────────────────────────────────────────────────

@login_required
def timetable_list(request):
    section_id = request.GET.get('section', '')
    sections = Section.objects.select_related('grade').all()
    timetables = []
    selected_section = None
    days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri']
    if section_id:
        selected_section = get_object_or_404(Section, pk=section_id)
        timetables = selected_section.timetables.select_related('subject', 'teacher').order_by('day', 'start_time')
    return render(request, 'school/timetable_list.html', {
        'sections': sections, 'timetables': timetables,
        'selected_section': selected_section, 'days': days, 'selected_section_id': section_id
    })


@login_required
def timetable_add(request):
    form = TimetableForm(request.POST or None)
    if form.is_valid():
        form.save()
        messages.success(request, 'Timetable entry added.')
        return redirect('timetable_list')
    return render(request, 'school/simple_form.html', {'form': form, 'title': 'Add Timetable Entry', 'back_url': 'timetable_list'})
# ─── ANNOUNCEMENTS ───────────────────────────────────────────────────────────

@login_required
def announcement_list(request):
    announcements = Announcement.objects.filter(is_active=True).select_related('created_by')
    return render(request, 'school/announcement_list.html', {'announcements': announcements})


@login_required
def announcement_add(request):
    form = AnnouncementForm(request.POST or None)
    if form.is_valid():
        ann = form.save(commit=False)
        ann.created_by = request.user
        ann.save()
        messages.success(request, 'Announcement published.')
        return redirect('announcement_list')
    return render(request, 'school/simple_form.html', {'form': form, 'title': 'Post Announcement', 'back_url': 'announcement_list'})


@login_required
def announcement_edit(request, pk):
    ann = get_object_or_404(Announcement, pk=pk)
    form = AnnouncementForm(request.POST or None, instance=ann)
    if form.is_valid():
        form.save()
        messages.success(request, 'Announcement updated.')
        return redirect('announcement_list')
    return render(request, 'school/simple_form.html', {'form': form, 'title': 'Edit Announcement', 'back_url': 'announcement_list'})


@login_required
def announcement_delete(request, pk):
    ann = get_object_or_404(Announcement, pk=pk)
    if request.method == 'POST':
        ann.is_active = False
        ann.save()
        messages.success(request, 'Announcement removed.')
        return redirect('announcement_list')
    return render(request, 'school/confirm_delete.html', {'object': ann, 'name': ann.title})
# ─── EVENTS ──────────────────────────────────────────────────────────────────

@login_required
def event_list(request):
    events = Event.objects.order_by('date')
    return render(request, 'school/event_list.html', {'events': events})


@login_required
def event_add(request):
    form = EventForm(request.POST or None)
    if form.is_valid():
        event = form.save(commit=False)
        event.created_by = request.user
        event.save()
        messages.success(request, 'Event added.')
        return redirect('event_list')
    return render(request, 'school/simple_form.html', {'form': form, 'title': 'Add Event', 'back_url': 'event_list'})


# ─── LEAVE REQUESTS ──────────────────────────────────────────────────────────

@login_required
def leave_list(request):
    leaves = LeaveRequest.objects.select_related('student', 'staff').order_by('-start_date')
    return render(request, 'school/leave_list.html', {'leaves': leaves})


@login_required
def leave_add(request):
    form = LeaveRequestForm(request.POST or None)
    if form.is_valid():
        form.save()
        messages.success(request, 'Leave request submitted.')
        return redirect('leave_list')
    return render(request, 'school/simple_form.html', {'form': form, 'title': 'Submit Leave Request', 'back_url': 'leave_list'})


@login_required
def leave_review(request, pk):
    leave = get_object_or_404(LeaveRequest, pk=pk)
    if request.method == 'POST':
        status = request.POST.get('status')
        if status in ['approved', 'rejected']:
            leave.status = status
            leave.reviewed_by = request.user
            leave.reviewed_at = timezone.now()
            leave.save()
            messages.success(request, f'Leave request {status}.')
    return redirect('leave_list')


# ─── REPORTS ─────────────────────────────────────────────────────────────────

@login_required
def reports_dashboard(request):
    return render(request, 'school/reports_dashboard.html')


@login_required
def report_students(request):
    grade_id = request.GET.get('grade', '')
    grades = Grade.objects.all()
    data = {}
    if grade_id:
        grade = get_object_or_404(Grade, pk=grade_id)
        sections = grade.sections.annotate(student_count=Count('students'))
        data = {'grade': grade, 'sections': sections}
    return render(request, 'school/report_students.html', {'grades': grades, 'data': data, 'selected_grade': grade_id})


@login_required
def report_finance(request):
    total_collected = FeePayment.objects.filter(status='paid').aggregate(t=Sum('amount_paid'))['t'] or 0
    total_pending = FeePayment.objects.filter(status__in=['pending','overdue']).aggregate(t=Sum('amount_due'))['t'] or 0
    by_type = FeePayment.objects.filter(status='paid').values('fee_structure__fee_type').annotate(total=Sum('amount_paid'))
    return render(request, 'school/report_finance.html', {
        'total_collected': total_collected,
        'total_pending': total_pending,
        'by_type': by_type
    })


# ─── ACADEMIC YEARS ──────────────────────────────────────────────────────────

@login_required
def academic_year_list(request):
    years = AcademicYear.objects.all()
    return render(request, 'school/academic_year_list.html', {'years': years})


@login_required
def academic_year_add(request):
    form = AcademicYearForm(request.POST or None)
    if form.is_valid():
        form.save()
        messages.success(request, 'Academic year added.')
        return redirect('academic_year_list')
    return render(request, 'school/simple_form.html', {'form': form, 'title': 'Add Academic Year', 'back_url': 'academic_year_list'})

def register_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    form = RegisterForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        user = form.save()
        login(request, user)
        messages.success(request, f'Account created! Welcome, {user.get_full_name() or user.username}.')
        return redirect('dashboard')
    return render(request, 'school/register.html', {'form': form})