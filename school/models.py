from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone


class User(AbstractUser):
    ROLE_CHOICES = [
        ('admin', 'Admin'),
        ('principal', 'Principal'),
        ('teacher', 'Teacher'),
        ('accountant', 'Accountant'),
        ('parent', 'Parent'),
        ('student', 'Student'),
    ]
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='teacher')
    phone = models.CharField(max_length=20, blank=True)
    address = models.TextField(blank=True)
    photo = models.ImageField(upload_to='users/', blank=True, null=True)

    def __str__(self):
        return f"{self.get_full_name()} ({self.role})"


class AcademicYear(models.Model):
    name = models.CharField(max_length=20)  # e.g. 2024/2025
    start_date = models.DateField()
    end_date = models.DateField()
    is_current = models.BooleanField(default=False)

    def __str__(self):
        return self.name


class Grade(models.Model):
    name = models.CharField(max_length=50)  # e.g. Grade 1
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name


class Section(models.Model):
    grade = models.ForeignKey(Grade, on_delete=models.CASCADE, related_name='sections')
    name = models.CharField(max_length=10)  # e.g. A, B, C
    class_teacher = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='class_sections')
    academic_year = models.ForeignKey(AcademicYear, on_delete=models.CASCADE)
    capacity = models.IntegerField(default=30)

    def __str__(self):
        return f"{self.grade.name} - {self.name}"


class Subject(models.Model):
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=20, unique=True)
    grade = models.ForeignKey(Grade, on_delete=models.CASCADE, related_name='subjects')
    teacher = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='subjects')
    description = models.TextField(blank=True)

    def __str__(self):
        return f"{self.name} ({self.grade.name})"


class Student(models.Model):
    GENDER_CHOICES = [('M', 'Male'), ('F', 'Female')]
    BLOOD_GROUPS = [('A+','A+'),('A-','A-'),('B+','B+'),('B-','B-'),('O+','O+'),('O-','O-'),('AB+','AB+'),('AB-','AB-')]

    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)
    student_id = models.CharField(max_length=20, unique=True)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    date_of_birth = models.DateField()
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES)
    blood_group = models.CharField(max_length=3, choices=BLOOD_GROUPS, blank=True)
    photo = models.ImageField(upload_to='students/', blank=True, null=True)
    section = models.ForeignKey(Section, on_delete=models.SET_NULL, null=True, related_name='students')
    admission_date = models.DateField(default=timezone.now)
    address = models.TextField()
    is_active = models.BooleanField(default=True)

    # Guardian Info
    guardian_name = models.CharField(max_length=100)
    guardian_phone = models.CharField(max_length=20)
    guardian_email = models.EmailField(blank=True)
    guardian_relationship = models.CharField(max_length=50)

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.student_id})"

    def get_full_name(self):
        return f"{self.first_name} {self.last_name}"


class Attendance(models.Model):
    STATUS_CHOICES = [('present','Present'),('absent','Absent'),('late','Late'),('excused','Excused')]
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='attendances')
    date = models.DateField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='present')
    section = models.ForeignKey(Section, on_delete=models.CASCADE)
    remarks = models.CharField(max_length=200, blank=True)
    marked_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)

    class Meta:
        unique_together = ['student', 'date']

    def __str__(self):
        return f"{self.student} - {self.date} - {self.status}"


class Exam(models.Model):
    EXAM_TYPES = [('midterm','Mid Term'),('final','Final'),('quiz','Quiz'),('assignment','Assignment')]
    name = models.CharField(max_length=100)
    exam_type = models.CharField(max_length=20, choices=EXAM_TYPES)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    section = models.ForeignKey(Section, on_delete=models.CASCADE)
    date = models.DateField()
    total_marks = models.DecimalField(max_digits=6, decimal_places=2)
    passing_marks = models.DecimalField(max_digits=6, decimal_places=2)
    academic_year = models.ForeignKey(AcademicYear, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.name} - {self.subject.name}"


class Result(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='results')
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE, related_name='results')
    marks_obtained = models.DecimalField(max_digits=6, decimal_places=2)
    remarks = models.CharField(max_length=200, blank=True)

    class Meta:
        unique_together = ['student', 'exam']

    @property
    def percentage(self):
        return (self.marks_obtained / self.exam.total_marks) * 100

    @property
    def grade_letter(self):
        p = self.percentage
        if p >= 90: return 'A+'
        elif p >= 80: return 'A'
        elif p >= 70: return 'B'
        elif p >= 60: return 'C'
        elif p >= 50: return 'D'
        return 'F'

    def __str__(self):
        return f"{self.student} - {self.exam} - {self.marks_obtained}"


class FeeStructure(models.Model):
    FEE_TYPES = [('tuition','Tuition'),('transport','Transport'),('books','Books'),('uniform','Uniform'),('activity','Activity'),('other','Other')]
    name = models.CharField(max_length=100)
    fee_type = models.CharField(max_length=20, choices=FEE_TYPES)
    grade = models.ForeignKey(Grade, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    academic_year = models.ForeignKey(AcademicYear, on_delete=models.CASCADE)
    due_day = models.IntegerField(default=5)  # day of month

    def __str__(self):
        return f"{self.name} - {self.grade.name} - {self.amount}"


class FeePayment(models.Model):
    STATUS_CHOICES = [('paid','Paid'),('partial','Partial'),('pending','Pending'),('overdue','Overdue')]
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='payments')
    fee_structure = models.ForeignKey(FeeStructure, on_delete=models.CASCADE)
    amount_due = models.DecimalField(max_digits=10, decimal_places=2)
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    payment_date = models.DateField(null=True, blank=True)
    due_date = models.DateField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    receipt_number = models.CharField(max_length=50, unique=True, blank=True)
    payment_method = models.CharField(max_length=50, blank=True)
    recorded_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return f"{self.student} - {self.fee_structure.name} - {self.status}"


class Announcement(models.Model):
    AUDIENCE_CHOICES = [('all','Everyone'),('teachers','Teachers'),('parents','Parents'),('students','Students')]
    title = models.CharField(max_length=200)
    content = models.TextField()
    audience = models.CharField(max_length=20, choices=AUDIENCE_CHOICES, default='all')
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title


class Timetable(models.Model):
    DAYS = [('Mon','Monday'),('Tue','Tuesday'),('Wed','Wednesday'),('Thu','Thursday'),('Fri','Friday')]
    section = models.ForeignKey(Section, on_delete=models.CASCADE, related_name='timetables')
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    teacher = models.ForeignKey(User, on_delete=models.CASCADE)
    day = models.CharField(max_length=3, choices=DAYS)
    start_time = models.TimeField()
    end_time = models.TimeField()

    def __str__(self):
        return f"{self.section} - {self.subject} - {self.day}"


class Event(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    location = models.CharField(max_length=200, blank=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['date']

    def __str__(self):
        return self.title


class LeaveRequest(models.Model):
    STATUS_CHOICES = [('pending','Pending'),('approved','Approved'),('rejected','Rejected')]
    LEAVE_TYPES = [('sick','Sick Leave'),('personal','Personal'),('emergency','Emergency'),('other','Other')]
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='leave_requests', null=True, blank=True)
    staff = models.ForeignKey(User, on_delete=models.CASCADE, related_name='leave_requests', null=True, blank=True)
    leave_type = models.CharField(max_length=20, choices=LEAVE_TYPES)
    start_date = models.DateField()
    end_date = models.DateField()
    reason = models.TextField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    reviewed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='reviewed_leaves')
    reviewed_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        name = self.student or self.staff
        return f"{name} - {self.leave_type} - {self.status}"