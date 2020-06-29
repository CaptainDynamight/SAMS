from django.shortcuts import render, redirect
from django.http import HttpResponse
from .models import Student, Course, Faculty, Attendance
import datetime
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login
from itertools import chain
from django.core.mail import send_mail
from django.conf import settings
from .message_api import sendPostRequest

# Create your views here.
URL = 'https://www.160by2.com/api/v1/sendCampaign'


def login_module(request):
    return render(request, 'Registration/login.html')


def home(request):
    if request.user.is_authenticated:
        faculty = Faculty.objects.filter(faculty_id=request.user)[0]
        context = {
            'dep_id': Faculty.objects.filter(faculty_id=request.user).values_list("dep_id")[0][0],
            'course_list': Course.objects.filter(faculty_id=faculty),
        }
        return render(request, 'Master/main.html', context=context)
    else:
        return render(request, 'Master/main.html')


def redirect_home(request):
    return redirect('/')


def sendMsg(date, absentees, no_of_absentees):
    absentees_phone = []
    absentees_name = []
    absentees_sem = []
    attendance_percent = []
    for x in absentees:
        data = Student.objects.filter(usn=x)[0]
        absentees_attendance = Attendance.objects.filter(usn=x)[0]
        attendance_percent.append(str(absentees_attendance.percent))
        absentees_phone.append(str(data.parent_phone))
        absentees_name.append(str(data.name))
        absentees_sem.append(str(data.sem))

    for z in range(no_of_absentees):
        mobile_no = str(absentees_phone[z])
        message = "You ward %s studying in Semester %s has not attended the classes on %s and is currently having " \
                  "the attendance percentage of %s.\n-Dr. Manjunath R\n HOD, Dept of CSE\n RRIT\n" % \
                  (absentees_name[z], absentees_sem[z], date, attendance_percent[z])
        sendPostRequest(URL, 'your key', 'your key', 'stage', mobile_no, 'identifier', message)


def create_log(request, attendees, no_of_attendees, course_id, period, msgtoggle):
    faculty = Faculty.objects.filter(faculty_id=request.user).values_list('id')[0][0]
    total_students = Attendance.objects.filter(course=course_id).filter(faculty_id=faculty).values_list('usn_id')
    total_students = [x[0] for x in total_students]
    total_names = Student.objects.filter(usn__in=total_students).values_list('name')
    total_names = [x[0] for x in total_names]
    total_names.sort()
    total_students.sort()
    attendees_names = Student.objects.filter(usn__in=attendees).values_list('name')
    attendees_names = [x[0] for x in attendees_names]
    absentees = list(set(total_students)-set(attendees))
    absentees.sort()
    absentees_names = Student.objects.filter(usn__in=absentees).values_list('name')
    absentees_names = [x[0] for x in absentees_names]
    no_of_absentees = len(absentees)
    date = datetime.datetime.now()
    date = date.strftime("%d %B %Y")
    if msgtoggle == '1':
        sendMsg(date, absentees, no_of_absentees)
    """filename = './Logs/%s.txt' % course_id
    try:
        file = open(filename, 'x')
        file.write('ATTENDANCE LOG COURSE %s \n\n\n' % course_id)
    except:
        file = open(filename, 'a')
    file.write('\n%s\nPeriod : %s\nNumber of Attendees : %i\nNumber of Absentees : %i\n\nAttendees :\n' % (date, period, no_of_attendees, no_of_absentees))
    for x, y in zip(attendees, attendees_names):
        file.write('%s \t %s \n' % (x, y))
    file.write('\nAbsentees :\n')
    for x, y in zip(absentees, absentees_names):
        file.write('%s \t %s \n' % (x, y))
    file.write('--------------------------------------------------------')
    file.close()"""


def user_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(username=username, password=password)
        if user:
            if user.is_active:
                login(request, user)
                return redirect('/')
            else:
                return HttpResponse("Your account was inactive.")
        else:
            print("Someone tried to login and failed.")
            print("They used username: {} and password: {}".format(username, password))
            return HttpResponse("Invalid login details given")
    else:
        return render(request, 'registration/login.html')


@login_required(login_url='/accounts/login/')
def mark_attendance(request, course_id):
    dummy = Faculty.objects.filter(faculty_id=request.user)[0]
    faculty = Faculty.objects.filter(faculty_id=request.user).values_list('id')[0][0]
    student = Attendance.objects.filter(course=course_id).filter(faculty_id=faculty).values_list('usn_id')
    student = [x[0] for x in student]
    name = Student.objects.filter(usn__in=student).values_list('name')
    name = [x[0] for x in name]
    name.sort()
    student.sort()
    context = {
        'title': '| Attendance |',
        'students': Attendance.objects.filter(course=course_id).filter(faculty_id=faculty),
        'course': course_id,
        'names': Student.objects.filter(usn__in=student).values_list('name'),
        'zip_data': zip(student, name),
        'course_list': Course.objects.filter(faculty_id=dummy),
        'dep_id': Faculty.objects.filter(faculty_id=request.user).values_list("dep_id")[0][0],
    }
    return render(request, 'Master/attendance.html', context=context)


@login_required(login_url='/accounts/login/')
def attendance_submit(request):
    course = request.POST.get('course')
    period = request.POST.get('period')
    msgtoggle = request.POST.get('msgtoggle')
    attendees = request.POST.getlist('present')
    no_of_attendees = len(attendees)
    create_log(request, attendees, no_of_attendees, course, period, msgtoggle)
    course_total = Course.objects.filter(course_id=course)[0]
    course_total.total_classes += 1
    course_total.save()
    for i in attendees:
        s = Student.objects.filter(usn=i)[0]
        attendance = Attendance.objects.filter(usn=s).filter(course_id=course)[0]
        attendance.current_attendance += 1
        attendance.save()
    students_total = Attendance.objects.filter(course_id=course).values_list('usn_id')
    students_total = [x[0] for x in students_total]
    for i in students_total:
        student = Attendance.objects.filter(course_id=course).filter(usn=i)[0]
        student.percent = (student.current_attendance / course_total.total_classes) * 100
        student.save()
    return redirect('/')


def contact(request):
    if request.user.is_authenticated:
        faculty = Faculty.objects.filter(faculty_id=request.user)[0]
        context = {
            'dep_id': Faculty.objects.filter(faculty_id=request.user).values_list("dep_id")[0][0],
            'course_list': Course.objects.filter(faculty_id=faculty),
        }
        return render(request, 'Master/contact.html', context=context)
    else:
        return render(request, 'Master/contact.html')


def contact_submit(request):
    subject = "SAMS - Query" + "[" + request.POST.get('subject') + "]"
    message = "NAME : " + request.POST.get('name') + "\nEMAIL_ID : " + request.POST.get('email') + "\nMESSAGE : \n" + request.POST.get('message')
    email_from = settings.EMAIL_HOST_USER
    recipient_list = ['gzerostudios@gmail.com', ]
    send_mail(subject, message, email_from, recipient_list, fail_silently=False)
    return redirect('/')


@login_required(login_url='/accounts/login/')
def timetable(request, dep_id, sem):
    dummy = Faculty.objects.filter(faculty_id=request.user)[0]
    table = {
        'CSE': {
            'sem1': [['', '', '', '', '', ''],
                     ['', '', '', '', '', ''],
                     ['', '', '', '', '', ''],
                     ['', '', '', '', '', ''],
                     ['', '', '', '', '', ''],
                     ['', '', '', '', '', ''],
                     ['', '', '', '', '', '']],

            'sem2': [['', '', '', '', '', ''],
                     ['', '', '', '', '', ''],
                     ['', '', '', '', '', ''],
                     ['', '', '', '', '', ''],
                     ['', '', '', '', '', ''],
                     ['', '', '', '', '', ''],
                     ['', '', '', '', '', '']],

            'sem3': [['18CS36', '18CSL37', '18CS35', '18CS35', '18CS34', '18CS32'],
                     ['18CS33', '18CSL38', '18CS32', '18MAT31', '18CS33', '18MAT31'],
                     ['18CS32', 'E-LEARNING', '18MAT31', '18CS32', '18CS35', '18CS34'],
                     ['18CS34', '18MAT31', '18CS36', '18MAT31', '18CS36', '18CS36'],
                     ['18CSL37', '18CPH39', '18CS34', '18CS36', '18CSL37', ''],
                     ['18CSL38', '18CS35', 'DIP MATHS', '18CS33', '18CSL38', ''],
                     ['E-LEARNING', '18CS33', 'DIP MATHS', 'REMEDIAL', 'E-LEARNING', '']],

            'sem4': [['', '', '', '', '', ''],
                     ['', '', '', '', '', ''],
                     ['', '', '', '', '', ''],
                     ['', '', '', '', '', ''],
                     ['', '', '', '', '', ''],
                     ['', '', '', '', '', ''],
                     ['', '', '', '', '', '']],

            'sem5': [['17CS562', '17CS551', '17CS51', '17CSL57', '17CS562', '17CS53'],
                     ['17CS51', '17CS53', '17CS52', '17CSL58', '17CS52', '17CS551'],
                     ['17CS551', '17CS52', '17CS551', 'E-LEARNING', '17CS53', '17CS54'],
                     ['17CS54', '17CS54', '17CS562', '17CS54', '17CS54', '17CS51'],
                     ['17CSL57', '17CS53', 'PLACEMENT', '17CS51', '17CSL57', ''],
                     ['17CSL58', '17CS52', 'PLACEMENT', '17CS52', '17CSL58', ''],
                     ['E-LEARNING', '17CS562', 'PLACEMENT', '17CS53', 'E-LEARNING', '']],

            'sem6': [['', '', '', '', '', ''],
                     ['', '', '', '', '', ''],
                     ['', '', '', '', '', ''],
                     ['', '', '', '', '', ''],
                     ['', '', '', '', '', ''],
                     ['', '', '', '', '', ''],
                     ['', '', '', '', '', '']],

            'sem7': [['', '', '', '', '', ''],
                     ['', '', '', '', '', ''],
                     ['', '', '', '', '', ''],
                     ['', '', '', '', '', ''],
                     ['', '', '', '', '', ''],
                     ['', '', '', '', '', ''],
                     ['', '', '', '', '', '']],

            'sem8': [['', '', '', '', '', ''],
                     ['', '', '', '', '', ''],
                     ['', '', '', '', '', ''],
                     ['', '', '', '', '', ''],
                     ['', '', '', '', '', ''],
                     ['', '', '', '', '', ''],
                     ['', '', '', '', '', '']],
        },

        'CE': {
            'sem1': [['', '', '', '', '', ''],
                     ['', '', '', '', '', ''],
                     ['', '', '', '', '', ''],
                     ['', '', '', '', '', ''],
                     ['', '', '', '', '', ''],
                     ['', '', '', '', '', ''],
                     ['', '', '', '', '', '']],

            'sem2': [['', '', '', '', '', ''],
                     ['', '', '', '', '', ''],
                     ['', '', '', '', '', ''],
                     ['', '', '', '', '', ''],
                     ['', '', '', '', '', ''],
                     ['', '', '', '', '', ''],
                     ['', '', '', '', '', '']],

            'sem3': [['', '', '', '', '', ''],
                     ['', '', '', '', '', ''],
                     ['', '', '', '', '', ''],
                     ['', '', '', '', '', ''],
                     ['', '', '', '', '', ''],
                     ['', '', '', '', '', ''],
                     ['', '', '', '', '', '']],

            'sem4': [['', '', '', '', '', ''],
                     ['', '', '', '', '', ''],
                     ['', '', '', '', '', ''],
                     ['', '', '', '', '', ''],
                     ['', '', '', '', '', ''],
                     ['', '', '', '', '', ''],
                     ['', '', '', '', '', '']],

            'sem5': [['', '', '', '', '', ''],
                     ['', '', '', '', '', ''],
                     ['', '', '', '', '', ''],
                     ['', '', '', '', '', ''],
                     ['', '', '', '', '', ''],
                     ['', '', '', '', '', ''],
                     ['', '', '', '', '', '']],

            'sem6': [['', '', '', '', '', ''],
                     ['', '', '', '', '', ''],
                     ['', '', '', '', '', ''],
                     ['', '', '', '', '', ''],
                     ['', '', '', '', '', ''],
                     ['', '', '', '', '', ''],
                     ['', '', '', '', '', '']],

            'sem7': [['', '', '', '', '', ''],
                     ['', '', '', '', '', ''],
                     ['', '', '', '', '', ''],
                     ['', '', '', '', '', ''],
                     ['', '', '', '', '', ''],
                     ['', '', '', '', '', ''],
                     ['', '', '', '', '', '']],

            'sem8': [['', '', '', '', '', ''],
                     ['', '', '', '', '', ''],
                     ['', '', '', '', '', ''],
                     ['', '', '', '', '', ''],
                     ['', '', '', '', '', ''],
                     ['', '', '', '', '', ''],
                     ['', '', '', '', '', '']],
        },

        'EEE': {
            'sem1': [['', '', '', '', '', ''],
                     ['', '', '', '', '', ''],
                     ['', '', '', '', '', ''],
                     ['', '', '', '', '', ''],
                     ['', '', '', '', '', ''],
                     ['', '', '', '', '', ''],
                     ['', '', '', '', '', '']],

            'sem2': [['', '', '', '', '', ''],
                     ['', '', '', '', '', ''],
                     ['', '', '', '', '', ''],
                     ['', '', '', '', '', ''],
                     ['', '', '', '', '', ''],
                     ['', '', '', '', '', ''],
                     ['', '', '', '', '', '']],

            'sem3': [['', '', '', '', '', ''],
                     ['', '', '', '', '', ''],
                     ['', '', '', '', '', ''],
                     ['', '', '', '', '', ''],
                     ['', '', '', '', '', ''],
                     ['', '', '', '', '', ''],
                     ['', '', '', '', '', '']],

            'sem4': [['', '', '', '', '', ''],
                     ['', '', '', '', '', ''],
                     ['', '', '', '', '', ''],
                     ['', '', '', '', '', ''],
                     ['', '', '', '', '', ''],
                     ['', '', '', '', '', ''],
                     ['', '', '', '', '', '']],

            'sem5': [['', '', '', '', '', ''],
                     ['', '', '', '', '', ''],
                     ['', '', '', '', '', ''],
                     ['', '', '', '', '', ''],
                     ['', '', '', '', '', ''],
                     ['', '', '', '', '', ''],
                     ['', '', '', '', '', '']],

            'sem6': [['', '', '', '', '', ''],
                     ['', '', '', '', '', ''],
                     ['', '', '', '', '', ''],
                     ['', '', '', '', '', ''],
                     ['', '', '', '', '', ''],
                     ['', '', '', '', '', ''],
                     ['', '', '', '', '', '']],

            'sem7': [['', '', '', '', '', ''],
                     ['', '', '', '', '', ''],
                     ['', '', '', '', '', ''],
                     ['', '', '', '', '', ''],
                     ['', '', '', '', '', ''],
                     ['', '', '', '', '', ''],
                     ['', '', '', '', '', '']],

            'sem8': [['', '', '', '', '', ''],
                     ['', '', '', '', '', ''],
                     ['', '', '', '', '', ''],
                     ['', '', '', '', '', ''],
                     ['', '', '', '', '', ''],
                     ['', '', '', '', '', ''],
                     ['', '', '', '', '', '']],
        },

        'ECE': {
            'sem1': [['', '', '', '', '', ''],
                     ['', '', '', '', '', ''],
                     ['', '', '', '', '', ''],
                     ['', '', '', '', '', ''],
                     ['', '', '', '', '', ''],
                     ['', '', '', '', '', ''],
                     ['', '', '', '', '', '']],

            'sem2': [['', '', '', '', '', ''],
                     ['', '', '', '', '', ''],
                     ['', '', '', '', '', ''],
                     ['', '', '', '', '', ''],
                     ['', '', '', '', '', ''],
                     ['', '', '', '', '', ''],
                     ['', '', '', '', '', '']],

            'sem3': [['', '', '', '', '', ''],
                     ['', '', '', '', '', ''],
                     ['', '', '', '', '', ''],
                     ['', '', '', '', '', ''],
                     ['', '', '', '', '', ''],
                     ['', '', '', '', '', ''],
                     ['', '', '', '', '', '']],

            'sem4': [['', '', '', '', '', ''],
                     ['', '', '', '', '', ''],
                     ['', '', '', '', '', ''],
                     ['', '', '', '', '', ''],
                     ['', '', '', '', '', ''],
                     ['', '', '', '', '', ''],
                     ['', '', '', '', '', '']],

            'sem5': [['', '', '', '', '', ''],
                     ['', '', '', '', '', ''],
                     ['', '', '', '', '', ''],
                     ['', '', '', '', '', ''],
                     ['', '', '', '', '', ''],
                     ['', '', '', '', '', ''],
                     ['', '', '', '', '', '']],

            'sem6': [['', '', '', '', '', ''],
                     ['', '', '', '', '', ''],
                     ['', '', '', '', '', ''],
                     ['', '', '', '', '', ''],
                     ['', '', '', '', '', ''],
                     ['', '', '', '', '', ''],
                     ['', '', '', '', '', '']],

            'sem7': [['', '', '', '', '', ''],
                     ['', '', '', '', '', ''],
                     ['', '', '', '', '', ''],
                     ['', '', '', '', '', ''],
                     ['', '', '', '', '', ''],
                     ['', '', '', '', '', ''],
                     ['', '', '', '', '', '']],

            'sem8': [['', '', '', '', '', ''],
                     ['', '', '', '', '', ''],
                     ['', '', '', '', '', ''],
                     ['', '', '', '', '', ''],
                     ['', '', '', '', '', ''],
                     ['', '', '', '', '', ''],
                     ['', '', '', '', '', '']],
        },

        'ISE': {
            'sem1': [['', '', '', '', '', ''],
                     ['', '', '', '', '', ''],
                     ['', '', '', '', '', ''],
                     ['', '', '', '', '', ''],
                     ['', '', '', '', '', ''],
                     ['', '', '', '', '', ''],
                     ['', '', '', '', '', '']],

            'sem2': [['', '', '', '', '', ''],
                     ['', '', '', '', '', ''],
                     ['', '', '', '', '', ''],
                     ['', '', '', '', '', ''],
                     ['', '', '', '', '', ''],
                     ['', '', '', '', '', ''],
                     ['', '', '', '', '', '']],

            'sem3': [['', '', '', '', '', ''],
                     ['', '', '', '', '', ''],
                     ['', '', '', '', '', ''],
                     ['', '', '', '', '', ''],
                     ['', '', '', '', '', ''],
                     ['', '', '', '', '', ''],
                     ['', '', '', '', '', '']],

            'sem4': [['', '', '', '', '', ''],
                     ['', '', '', '', '', ''],
                     ['', '', '', '', '', ''],
                     ['', '', '', '', '', ''],
                     ['', '', '', '', '', ''],
                     ['', '', '', '', '', ''],
                     ['', '', '', '', '', '']],

            'sem5': [['', '', '', '', '', ''],
                     ['', '', '', '', '', ''],
                     ['', '', '', '', '', ''],
                     ['', '', '', '', '', ''],
                     ['', '', '', '', '', ''],
                     ['', '', '', '', '', ''],
                     ['', '', '', '', '', '']],

            'sem6': [['', '', '', '', '', ''],
                     ['', '', '', '', '', ''],
                     ['', '', '', '', '', ''],
                     ['', '', '', '', '', ''],
                     ['', '', '', '', '', ''],
                     ['', '', '', '', '', ''],
                     ['', '', '', '', '', '']],

            'sem7': [['', '', '', '', '', ''],
                     ['', '', '', '', '', ''],
                     ['', '', '', '', '', ''],
                     ['', '', '', '', '', ''],
                     ['', '', '', '', '', ''],
                     ['', '', '', '', '', ''],
                     ['', '', '', '', '', '']],

            'sem8': [['', '', '', '', '', ''],
                     ['', '', '', '', '', ''],
                     ['', '', '', '', '', ''],
                     ['', '', '', '', '', ''],
                     ['', '', '', '', '', ''],
                     ['', '', '', '', '', ''],
                     ['', '', '', '', '', '']],
        },

        'ME': {
            'sem1': [['', '', '', '', '', ''],
                     ['', '', '', '', '', ''],
                     ['', '', '', '', '', ''],
                     ['', '', '', '', '', ''],
                     ['', '', '', '', '', ''],
                     ['', '', '', '', '', ''],
                     ['', '', '', '', '', '']],

            'sem2': [['', '', '', '', '', ''],
                     ['', '', '', '', '', ''],
                     ['', '', '', '', '', ''],
                     ['', '', '', '', '', ''],
                     ['', '', '', '', '', ''],
                     ['', '', '', '', '', ''],
                     ['', '', '', '', '', '']],

            'sem3': [['', '', '', '', '', ''],
                     ['', '', '', '', '', ''],
                     ['', '', '', '', '', ''],
                     ['', '', '', '', '', ''],
                     ['', '', '', '', '', ''],
                     ['', '', '', '', '', ''],
                     ['', '', '', '', '', '']],

            'sem4': [['', '', '', '', '', ''],
                     ['', '', '', '', '', ''],
                     ['', '', '', '', '', ''],
                     ['', '', '', '', '', ''],
                     ['', '', '', '', '', ''],
                     ['', '', '', '', '', ''],
                     ['', '', '', '', '', '']],

            'sem5': [['', '', '', '', '', ''],
                     ['', '', '', '', '', ''],
                     ['', '', '', '', '', ''],
                     ['', '', '', '', '', ''],
                     ['', '', '', '', '', ''],
                     ['', '', '', '', '', ''],
                     ['', '', '', '', '', '']],

            'sem6': [['', '', '', '', '', ''],
                     ['', '', '', '', '', ''],
                     ['', '', '', '', '', ''],
                     ['', '', '', '', '', ''],
                     ['', '', '', '', '', ''],
                     ['', '', '', '', '', ''],
                     ['', '', '', '', '', '']],

            'sem7': [['', '', '', '', '', ''],
                     ['', '', '', '', '', ''],
                     ['', '', '', '', '', ''],
                     ['', '', '', '', '', ''],
                     ['', '', '', '', '', ''],
                     ['', '', '', '', '', ''],
                     ['', '', '', '', '', '']],

            'sem8': [['', '', '', '', '', ''],
                     ['', '', '', '', '', ''],
                     ['', '', '', '', '', ''],
                     ['', '', '', '', '', ''],
                     ['', '', '', '', '', ''],
                     ['', '', '', '', '', ''],
                     ['', '', '', '', '', '']],
        },

        'BS': {
            'sem1': [['', '', '', '', '', ''],
                     ['', '', '', '', '', ''],
                     ['', '', '', '', '', ''],
                     ['', '', '', '', '', ''],
                     ['', '', '', '', '', ''],
                     ['', '', '', '', '', ''],
                     ['', '', '', '', '', '']],

            'sem2': [['', '', '', '', '', ''],
                     ['', '', '', '', '', ''],
                     ['', '', '', '', '', ''],
                     ['', '', '', '', '', ''],
                     ['', '', '', '', '', ''],
                     ['', '', '', '', '', ''],
                     ['', '', '', '', '', '']],

            'sem3': [['', '', '', '', '', ''],
                     ['', '', '', '', '', ''],
                     ['', '', '', '', '', ''],
                     ['', '', '', '', '', ''],
                     ['', '', '', '', '', ''],
                     ['', '', '', '', '', ''],
                     ['', '', '', '', '', '']],

            'sem4': [['', '', '', '', '', ''],
                     ['', '', '', '', '', ''],
                     ['', '', '', '', '', ''],
                     ['', '', '', '', '', ''],
                     ['', '', '', '', '', ''],
                     ['', '', '', '', '', ''],
                     ['', '', '', '', '', '']],

            'sem5': [['', '', '', '', '', ''],
                     ['', '', '', '', '', ''],
                     ['', '', '', '', '', ''],
                     ['', '', '', '', '', ''],
                     ['', '', '', '', '', ''],
                     ['', '', '', '', '', ''],
                     ['', '', '', '', '', '']],

            'sem6': [['', '', '', '', '', ''],
                     ['', '', '', '', '', ''],
                     ['', '', '', '', '', ''],
                     ['', '', '', '', '', ''],
                     ['', '', '', '', '', ''],
                     ['', '', '', '', '', ''],
                     ['', '', '', '', '', '']],

            'sem7': [['', '', '', '', '', ''],
                     ['', '', '', '', '', ''],
                     ['', '', '', '', '', ''],
                     ['', '', '', '', '', ''],
                     ['', '', '', '', '', ''],
                     ['', '', '', '', '', ''],
                     ['', '', '', '', '', '']],

            'sem8': [['', '', '', '', '', ''],
                     ['', '', '', '', '', ''],
                     ['', '', '', '', '', ''],
                     ['', '', '', '', '', ''],
                     ['', '', '', '', '', ''],
                     ['', '', '', '', '', ''],
                     ['', '', '', '', '', '']],
        },
    }
    course_id = list(set(chain(*table[dep_id][sem])))
    rem_list = ['', 'PLACEMENT', 'E-LEARNING', '18CPH39', 'DIP MATHS', '18MAT31', 'REMEDIAL']
    course_id = [x for x in course_id if x not in rem_list]
    course_id.sort()
    faculty_id = []
    faculty_name = []
    course_name = []
    for i in course_id:
        temp = Course.objects.values('faculty_id').get(course_id=i)['faculty_id']
        faculty_id.append(temp)
        temp1 = Faculty.objects.values('faculty_name').get(id=temp)['faculty_name']
        faculty_name.append(temp1)
        temp2 = Course.objects.values('course_name').get(course_id=i)['course_name']
        course_name.append(temp2)
    context = {
        'dep_id': dep_id,
        'year': sem,
        'timetable': table[dep_id][sem],
        'zip_data': zip(course_id, course_name, faculty_name),
        'course_list': Course.objects.filter(faculty_id=dummy)
    }
    return render(request, 'Master/timetable.html', context=context)


def sem_course_generator(sem):
    course_id = Course.objects.filter(sem=sem).values_list('course_id')
    course_id = [x[0] for x in course_id]
    course_id.sort()
    faculty_id = []
    faculty_name = []
    course_name = []
    for i in course_id:
        temp = Course.objects.values('faculty_id').get(course_id=i)['faculty_id']
        faculty_id.append(temp)
        temp1 = Faculty.objects.values('faculty_name').get(id=temp)['faculty_name']
        faculty_name.append(temp1)
        temp2 = Course.objects.values('course_name').get(course_id=i)['course_name']
        course_name.append(temp2)
    return course_id, course_name, faculty_name


@login_required(login_url='/accounts/login/')
def view_attendance(request):
    dummy = Faculty.objects.filter(faculty_id=request.user)[0]

    sem1_course_id, sem1_course_name, sem1_faculty_name = sem_course_generator(sem='1')
    sem2_course_id, sem2_course_name, sem2_faculty_name = sem_course_generator(sem='2')
    sem3_course_id, sem3_course_name, sem3_faculty_name = sem_course_generator(sem='3')
    sem4_course_id, sem4_course_name, sem4_faculty_name = sem_course_generator(sem='4')
    sem5_course_id, sem5_course_name, sem5_faculty_name = sem_course_generator(sem='5')
    sem6_course_id, sem6_course_name, sem6_faculty_name = sem_course_generator(sem='6')
    sem7_course_id, sem7_course_name, sem7_faculty_name = sem_course_generator(sem='7')
    sem8_course_id, sem8_course_name, sem8_faculty_name = sem_course_generator(sem='8')

    context = {
        'course_list': Course.objects.filter(faculty_id=dummy),
        'sem1_zip': zip(sem1_course_id, sem1_course_name, sem1_faculty_name),
        'sem2_zip': zip(sem2_course_id, sem2_course_name, sem2_faculty_name),
        'sem3_zip': zip(sem3_course_id, sem3_course_name, sem3_faculty_name),
        'sem4_zip': zip(sem4_course_id, sem4_course_name, sem4_faculty_name),
        'sem5_zip': zip(sem5_course_id, sem5_course_name, sem5_faculty_name),
        'sem6_zip': zip(sem6_course_id, sem6_course_name, sem6_faculty_name),
        'sem7_zip': zip(sem7_course_id, sem7_course_name, sem7_faculty_name),
        'sem8_zip': zip(sem8_course_id, sem8_course_name, sem8_faculty_name),
        'dep_id': Faculty.objects.filter(faculty_id=request.user).values_list("dep_id")[0][0],
    }
    return render(request, 'Master/view.html', context=context)


@login_required(login_url='/accounts/login/')
def course_view(request, course_id):
    dummy = Faculty.objects.filter(faculty_id=request.user)[0]
    temp = Course.objects.values('faculty_id').get(course_id=course_id)['faculty_id']
    total_students = Attendance.objects.filter(course_id=course_id).values('usn')
    total_students = [x['usn'] for x in total_students]
    total_students.sort()
    eligible_usn = []
    eligible_percent = []
    eligible_name = []
    eligible_class = []
    not_eligible_usn = []
    not_eligible_percent = []
    not_eligible_name = []
    not_eligible_class = []
    for i in total_students:
        student = Attendance.objects.filter(course_id=course_id).filter(usn=i)[0]
        student_names = Student.objects.values('name').get(usn=i)['name']
        if student.percent >= 85:
            eligible_name.append(student_names)
            eligible_usn.append(i)
            eligible_percent.append(student.percent)
            eligible_class.append(student.current_attendance)
        else:
            not_eligible_name.append(student_names)
            not_eligible_usn.append(i)
            not_eligible_percent.append(student.percent)
            not_eligible_class.append(student.current_attendance)
    context = {
        'course_list': Course.objects.filter(faculty_id=dummy),
        'course_id': course_id,
        'course_name': Course.objects.values('course_name').get(course_id=course_id)['course_name'],
        'faculty_name': Faculty.objects.values('faculty_name').get(id=temp)['faculty_name'],
        'total_classes': Course.objects.values('total_classes').get(course_id=course_id)['total_classes'],
        'eligible_zip': zip(eligible_usn, eligible_name, eligible_class, eligible_percent),
        'not_eligible_zip': zip(not_eligible_usn, not_eligible_name, not_eligible_class, not_eligible_percent),
        'dep_id': Faculty.objects.filter(faculty_id=request.user).values_list("dep_id")[0][0],
    }
    return render(request, 'Master/course_view.html', context=context)
