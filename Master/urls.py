from django.conf.urls import url, include
from django.urls import path
from django.contrib.auth import views as auth_views
from . import views


urlpatterns = [
    path('accounts/logout/', auth_views.LogoutView.as_view(next_page='/logout/')),
    path('accounts/', include('django.contrib.auth.urls')),
    url(r'^attendance_submit/$', views.attendance_submit, name='Master-attendance_submit'),
    url(r'^login_submit/$', views.user_login, name='Master-login_submit'),
    url(r'^contact/$', views.contact, name='Master-contact'),
    url(r'^view/$', views.view_attendance, name='Master-view'),
    url(r'^login/$', views.login_module, name='Master-login'),
    url(r'^logout/$', views.redirect_home, name='Master-logged_out'),
    path('mark_attendance/<str:course_id>/', views.mark_attendance, name='Master-mark_attendance'),
    path('timetable/<str:dep_id>/<str:sem>/', views.timetable, name='Master-timetable'),
    path('view/<str:course_id>/', views.course_view, name='Master-timetable'),
    url(r'^contact_submit/$', views.contact_submit, name='Master-contact_submit'),
    url(r'', views.home, name='Master-home'),
]
