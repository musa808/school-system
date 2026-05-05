from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import date, timedelta
from school.models import *
import random


class Command(BaseCommand):
    help = 'Creates demo data for the school management system'

    def handle(self, *args, **kwargs):
        self.stdout.write('Creating demo data...')

        # Academic Year
        year, _ = AcademicYear.objects.get_or_create(
            name='2024/2025',
            defaults={'start_date': date(2024, 9, 1), 'end_date': date(2025, 7, 31), 'is_current': True}
        )

        # Grades
        grade_names = ['Grade 1', 'Grade 2', 'Grade 3', 'Grade 4', 'Grade 5', 'Grade 6']
        grades = []
        for name in grade_names:
            g, _ = Grade.objects.get_or_create(name=name, defaults={'description': f'{name} level'})
            grades.append(g)

        # Admin user
        admin, created = User.objects.get_or_create(
            username='admin',
            defaults={'first_name': 'Admin', 'last_name': 'User', 'role': 'admin', 'is_staff': True, 'is_superuser': True}
        )
        if created:
            admin.set_password('admin123')
            admin.save()

        # Teachers
        teacher_data = [
            ('teacher1', 'Alice', 'Johnson', 'teacher'),
            ('teacher2', 'Bob', 'Smith', 'teacher'),
            ('teacher3', 'Carol', 'Davis', 'teacher'),
            ('principal1', 'David', 'Wilson', 'principal'),
            ('accountant1', 'Eve', 'Brown', 'accountant'),
        ]
        teachers = []
        for username, fn, ln, role in teacher_data:
            t, created = User.objects.get_or_create(
                username=username,
                defaults={'first_name': fn, 'last_name': ln, 'role': role, 'email': f'{username}@school.edu'}
            )
            if created:
                t.set_password('teacher123')
                t.save()
            teachers.append(t)

        # Sections
        sections = []
        for i, grade in enumerate(grades[:3]):
            for section_name in ['A', 'B']:
                teacher = teachers[i % 3]
                s, _ = Section.objects.get_or_create(
                    grade=grade, name=section_name, academic_year=year,
                    defaults={'class_teacher': teacher, 'capacity': 30}
                )
                sections.append(s)

        # Subjects
        subject_data = [
            ('Mathematics', 'MATH'), ('English', 'ENG'), ('Science', 'SCI'),
            ('Social Studies', 'SOC'), ('Art', 'ART'), ('Physical Education', 'PE'),
        ]
        for grade in grades[:3]:
            for i, (name, code) in enumerate(subject_data):
                Subject.objects.get_or_create(
                    name=name, grade=grade,
                    defaults={'code': f'{code}{grade.name[-1]}', 'teacher': teachers[i % 3]}
                )

        # Students
        first_names = ['James', 'Emma', 'Oliver', 'Ava', 'Noah', 'Sophia', 'Liam', 'Isabella', 'William', 'Mia']
        last_names = ['Anderson', 'Taylor', 'Moore', 'Jackson', 'Martin', 'Thompson', 'Garcia', 'White', 'Lee', 'Clark']
        guardians = ['Mary Anderson', 'John Taylor', 'Susan Moore', 'Robert Jackson', 'Linda Martin']

        student_count = 0
        for section in sections[:4]:
            for j in range(8):
                fname = first_names[(student_count + j) % len(first_names)]
                lname = last_names[(student_count + j) % len(last_names)]
                sid = f'STU{str(student_count + j + 1).zfill(4)}'
                Student.objects.get_or_create(
                    student_id=sid,
                    defaults={
                        'first_name': fname, 'last_name': lname,
                        'date_of_birth': date(2015, (j % 12) + 1, (j % 28) + 1),
                        'gender': 'M' if j % 2 == 0 else 'F',
                        'section': section,
                        'address': f'{j+1} School Street, City',
                        'guardian_name': guardians[j % len(guardians)],
                        'guardian_phone': f'555-{str(1000 + student_count + j)}',
                        'guardian_email': f'parent{student_count + j}@email.com',
                        'guardian_relationship': 'Parent',
                    }
                )
            student_count += 8

        # Fee Structures
        fee_types = [
            ('Tuition Fee', 'tuition', 500),
            ('Transport Fee', 'transport', 100),
            ('Books Fee', 'books', 80),
        ]
        for grade in grades[:3]:
            for name, ftype, amount in fee_types:
                FeeStructure.objects.get_or_create(
                    name=name, grade=grade, academic_year=year,
                    defaults={'fee_type': ftype, 'amount': amount, 'due_day': 5}
                )

        # Announcements
        ann_data = [
            ('Welcome Back!', 'Welcome to the new academic year 2024/2025. We look forward to a great year.', 'all'),
            ('Parent-Teacher Meeting', 'PTM scheduled for next Friday at 2 PM in the main hall.', 'parents'),
            ('Staff Development Day', 'Please note the staff training session on Saturday.', 'teachers'),
        ]
        for title, content, audience in ann_data:
            Announcement.objects.get_or_create(
                title=title,
                defaults={'content': content, 'audience': audience, 'created_by': admin}
            )

        # Events
        events_data = [
            ('Annual Sports Day', date.today() + timedelta(days=14), 'Main Sports Ground'),
            ('Science Fair', date.today() + timedelta(days=30), 'School Hall'),
            ('End of Term Concert', date.today() + timedelta(days=60), 'Auditorium'),
        ]
        for title, edate, location in events_data:
            Event.objects.get_or_create(
                title=title,
                defaults={'date': edate, 'location': location, 'created_by': admin}
            )

        self.stdout.write(self.style.SUCCESS(
            '\nDemo data created successfully!\n'
            'Login credentials:\n'
            '  Admin:      admin / admin123\n'
            '  Teacher:    teacher1 / teacher123\n'
            '  Principal:  principal1 / teacher123\n'
            '  Accountant: accountant1 / teacher123\n'
        ))