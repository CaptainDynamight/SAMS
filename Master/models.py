from django.db import models
from django.contrib.auth.models import User


class Student(models.Model):
    sem_choice = (
        (1, 'First'),
        (2, 'Second'),
        (3, 'Third'),
        (4, 'Fourth'),
        (5, 'Fifth'),
        (6, 'Sixth'),
        (7, 'Seventh'),
        (8, 'Eighth'),
    )
    usn = models.CharField(max_length=10, primary_key=True)
    name = models.CharField(max_length=40, null=False, default='')
    sem = models.IntegerField(choices=sem_choice, null=False, default=1)
    dep = models.ForeignKey('Department', on_delete=models.CASCADE)
    phone = models.CharField(max_length=12, null=False, default='')
    parent_phone = models.CharField(max_length=12, null=False, default='')

    def __str__(self):
        return self.usn


class Department(models.Model):
    dep_choice = (
        ('CE', 'Civil Engineering'),
        ('CSE', 'Computer Science Engineering'),
        ('EEE', 'Electrical Engineering'),
        ('ECE', 'Electronics and Communications Engineering'),
        ('ISE', 'Information Science Engineering'),
        ('ME', 'Mechanical Engineering'),
        ('BS', 'Basic Science'),
    )
    depname = models.CharField(max_length=3, choices=dep_choice, primary_key=True)
    dep_email = models.CharField(max_length=50, null=False, default='')
    dep_contact = models.CharField(max_length=10, null=False, default='')


class Faculty(models.Model):
    faculty = models.OneToOneField(to=User, on_delete=models.CASCADE)
    faculty_name = models.CharField(max_length=40)
    dep = models.ForeignKey('Department', on_delete=models.CASCADE)
    ph_no = models.CharField(max_length=10)

    def __str__(self):
        return self.faculty_name


class Course(models.Model):
    sem_choice = (
        (1, 'First'),
        (2, 'Second'),
        (3, 'Third'),
        (4, 'Fourth'),
        (5, 'Fifth'),
        (6, 'Sixth'),
        (7, 'Seventh'),
        (8, 'Eighth'),
    )
    course_id = models.CharField(max_length=7, primary_key=True)
    course_name = models.CharField(max_length=50, null=False, default='')
    dep = models.ForeignKey('Department', on_delete=models.CASCADE)
    faculty = models.ForeignKey('Faculty', on_delete=models.CASCADE)
    total_classes = models.IntegerField(null=False, default=0)
    sem = models.IntegerField(choices=sem_choice, null=False, default=1)

    def __str__(self):
        return self.course_id


class Attendance(models.Model):
    course = models.ForeignKey('Course', on_delete=models.CASCADE)
    faculty = models.ForeignKey('Faculty', on_delete=models.CASCADE)
    usn = models.ForeignKey('Student', on_delete=models.CASCADE, db_column='usn')
    current_attendance = models.IntegerField(null=False, default=0)
    percent = models.IntegerField(null=False, default=0)

    def __str___(self):
        return self.usn
