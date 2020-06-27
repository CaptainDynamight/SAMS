from django.contrib import admin
from .models import Student, Department, Faculty, Course, Attendance
# Register your models here.

admin.site.register(Student)
admin.site.register(Department)
admin.site.register(Faculty)
admin.site.register(Course)
admin.site.register(Attendance)
