"""
URL configuration for docappsystem project.
"""

from django.contrib import admin
from django.urls import path
from django.conf.urls.static import static
from django.conf import settings
from . import views, adminviews, docviews, userviews

urlpatterns = [
    # Admin site
    path('admin/', admin.site.urls),

    # Base and authentication
    path('base/', views.BASE, name='base'),
    path('login', views.LOGIN, name='login'),
    path('doLogin', views.doLogin, name='doLogin'),
    path('doLogout', views.doLogout, name='logout'),

    # Admin Panel
    path('Admin/AdminHome', adminviews.ADMINHOME, name='admin_home'),
    path('Admin/Specialization', adminviews.SPECIALIZATION, name='add_specilizations'),
    path('Admin/ManageSpecialization', adminviews.MANAGESPECIALIZATION, name='manage_specilizations'),
    path('Admin/DeleteSpecialization/<str:id>', adminviews.DELETE_SPECIALIZATION, name='delete_specilizations'),
    path('UpdateSpecialization/<str:id>', adminviews.UPDATE_SPECIALIZATION, name='update_specilizations'),
    path('UPDATE_Specialization_DETAILS', adminviews.UPDATE_SPECIALIZATION_DETAILS, name='update_specilizations_details'),
    path('Admin/DoctorList', adminviews.DoctorList, name='viewdoctorlist'),
    path('Admin/ViewDoctorDetails/<str:id>', adminviews.ViewDoctorDetails, name='viewdoctordetails'),
    path('Admin/DeleteDoctor/<str:id>', adminviews.DeleteDoctor, name='deletedoctor'),
    path('Admin/ViewDoctorAppointmentList/<str:id>', adminviews.ViewDoctorAppointmentList, name='viewdoctorappointmentlist'),
    path('Admin/ViewPatientDetails/<str:id>', adminviews.ViewPatientDetails, name='viewpatientdetails'),
    path('SearchDoctor', adminviews.Search_Doctor, name='search_doctor'),
    path('DoctorBetweenDateReport', adminviews.Doctor_Between_Date_Report, name='doctor_between_date_report'),

    # Website Page
    path('Website/update', adminviews.WEBSITE_UPDATE, name='website_update'),
    path('UPDATE_WEBSITE_DETAILS', adminviews.UPDATE_WEBSITE_DETAILS, name='update_website_details'),

    # Admin Payment & SMS Logs
    path('Admin/Payments/', adminviews.admin_payments, name='admin_payments'),
    path('Admin/SMSLogs/', adminviews.admin_sms_logs, name='admin_sms_logs'),

    # Doctor Panel
    path('docsignup/', docviews.DOCSIGNUP, name='docsignup'),
    path('Doctor/DocHome', docviews.DOCTORHOME, name='doctor_home'),
    path('Doctor/ViewAppointment', docviews.View_Appointment, name='view_appointment'),
    path('DoctorPatientAppointmentDetails/<str:id>', docviews.Patient_Appointment_Details, name='patientappointmentdetails'),
    path('AppointmentDetailsRemark/Update', docviews.Patient_Appointment_Details_Remark, name='patient_appointment_details_remark'),
    path('DoctorPatientApprovedAppointment', docviews.Patient_Approved_Appointment, name='patientapprovedappointment'),
    path('DoctorPatientCancelledAppointment', docviews.Patient_Cancelled_Appointment, name='patientcancelledappointment'),
    path('DoctorPatientNewAppointment', docviews.Patient_New_Appointment, name='patientnewappointment'),
    path('DoctorPatientListApprovedAppointment', docviews.Patient_List_Approved_Appointment, name='patientlistappointment'),
    path('DoctorAppointmentList/<str:id>', docviews.DoctorAppointmentList, name='doctorappointmentlist'),
    path('PatientAppointmentPrescription', docviews.Patient_Appointment_Prescription, name='patientappointmentprescription'),
    path('PatientAppointmentCompleted', docviews.Patient_Appointment_Completed, name='patientappointmentcompleted'),
    path('SearchAppointment', docviews.Search_Appointments, name='search_appointment'),
    path('BetweenDateReport', docviews.Between_Date_Report, name='between_date_report'),

    # User Panel
    path('userbase/', userviews.userbase, name='userbase'),
    path('', userviews.Index, name='index'),
    path('userappointment/', userviews.create_appointment, name='userappointment'),
    path('User_SearchAppointment', userviews.User_Search_Appointments, name='user_search_appointment'),
    path('ViewAppointmentDetails/<str:id>/', userviews.View_Appointment_Details, name='viewappointmentdetails'),

    # Payment
    path('payment-callback/', userviews.payment_callback, name='payment_callback'),
    path('appointment-success/<int:appointment_id>/', userviews.appointment_success, name='appointment_success'),
    path('dummy-payment/<int:appointment_id>/', userviews.dummy_payment_page, name='dummy_payment_page'),
    path('dummy-payment-process/<int:appointment_id>/<str:status>/', userviews.dummy_payment_process, name='dummy_payment_process'),

    # Profile
    path('Profile', views.PROFILE, name='profile'),
    path('Profile/update', views.PROFILE_UPDATE, name='profile_update'),
    path('Password', views.CHANGE_PASSWORD, name='change_password'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)