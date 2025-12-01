from django.urls import path
from . import views
from . import views_ai


from .views import (
    RegisterView,
    LoginUserAPIView,
    AssignedDoctorAvailabilityAPIView,
    AppointmentReasonsAPIView,
    AppointmentGenderChoicesAPIView,
    AppointmentBookingForChoicesAPIView,
    CreateAppointmentAPIView,
    MyAppointmentsAPIView,
    CancelAppointmentAPIView,
    EditAppointmentAPIView,
    DoctorListAPIView,
    RegisterPushTokenAPIView,
    DeleteAppointmentAPIView,
    UpdateProfileAPIView,
    NotificationListAPIView,  # add this import
    MarkNotificationReadAPIView,
    NotificationDetailAPIView,
    NotificationMarkReadView
    

)

urlpatterns = [
    # --- WEB ADMIN PANEL ROUTES ---
    path('', views.admin_login, name='admin_login'),
    path('dashboard/', views.admin_dashboard_view, name='admin_dashboard'),
    path('home/', views.admin_home, name='admin_home'),
    path('logout/', views.admin_logout, name='admin_logout'),
    path('admin-register/', views.admin_register, name='admin_register'), # ✅ renamed for admin only
    path('appointments/', views.monitor_appointments, name='monitor_appointments'),
    path('profile/', views.admin_profile, name='admin_profile'),
    path('manage-doctors-availability/', views.manage_doctors_availability, name='manage_doctors_availability'),
    path('doctor-overview-patients-record/', views.doctor_overview_patients_record, name='doctor_overview_patients_record'),
    path('notifications/', views.admin_notifications, name='admin_notifications'),
    path('notifications/mark-all-read/', views.mark_all_notifications_read, name='mark_all_notifications_read'),
    path('notifications/mark-read/<int:notification_id>/', views.mark_notification_read, name='mark_notification_read'),
    path('completed-appointments/', views.completed_appointments, name='completed_appointments'),
    path('update_status/', views.update_status, name='update_status'),


    # --- USER MANAGEMENT (Admin Panel) ---
    path('users/', views.admin_users, name='admin_users'),
    path('users/add/', views.add_user, name='add_user'),
    path('users/edit/<int:user_id>/', views.edit_user, name='edit_user'),
    path('users/delete/<int:user_id>/', views.delete_user, name='delete_user'),

    # --- ADMIN ACTIONS ---
    path('appointments/archive/', views.archive_appointment, name='archive_appointment'),
    path('patients/archive/', views.archive_patient, name='archive_patient'),
    path('manage-doctors-availability/set-availability/', views.set_doctor_availability, name='set_doctor_availability'),
    path('patient-details/<int:patient_id>/', views.get_patient_details, name='get_patient_details'),
    
    # DOCTORS PATHS (Fixed the missing 'add_doctor' entry here)
    path('manage-doctors-hub/', views.manage_doctors_hub_view, name='manage_doctors'),
    path('add-doctor/', views.add_doctor, name='add_doctor'), # <-- ADDED THIS MISSING ENTRY
    path('manage-doctors-availability/', views.manage_doctors_availability, name='manage_doctors_availability'),
    path('doctor-overview-patients-record/', views.doctor_overview_patients_record, name='doctor_overview_patients_record'),

    # --- API ENDPOINTS (for mobile app) ---
    path('api/register/', RegisterView.as_view(), name='api-register'),
    path('api/login/', LoginUserAPIView.as_view(), name='api-login'),
    path('api/update-profile/', UpdateProfileAPIView.as_view(), name='api-update-profile'),

    path('api/register-push-token/', RegisterPushTokenAPIView.as_view(), name='register-push-token'),
    path('api/assigned-availability/', AssignedDoctorAvailabilityAPIView.as_view(), name='api-assigned-availability'),
    path('api/doctors/', DoctorListAPIView.as_view(), name='api-doctor-list'),

    path('api/appointments/create/', CreateAppointmentAPIView.as_view(), name='create-appointment'),
    path('api/my-appointments/', MyAppointmentsAPIView.as_view(), name='my-appointments'),

    path('api/appointment/reasons/', AppointmentReasonsAPIView.as_view(), name='appointment_reasons_api'),
    path('api/appointment/genders/', AppointmentGenderChoicesAPIView.as_view(), name='appointment_genders_api'),
    path('api/appointment/booking-for/', AppointmentBookingForChoicesAPIView.as_view(), name='appointment_booking_for_api'),

    path('api/cancel-appointment/<int:pk>/', CancelAppointmentAPIView.as_view(), name='cancel-appointment'),
    path('api/edit-appointment/<int:pk>/', EditAppointmentAPIView.as_view(), name='edit-appointment'),
    path('api/delete-appointment/<int:pk>/', DeleteAppointmentAPIView.as_view(), name='delete-appointment'),
    path('api/notification/', NotificationListAPIView.as_view(), name='api-notification'),
    path('api/notification/<int:pk>/read/', MarkNotificationReadAPIView.as_view(), name='mark-notification-read'),
    path('notification/mark-all-read/', views.mark_all_read, name='mark-all-read'),
    path("api/classify-eye/", views_ai.classify_eye_image, name="classify_eye_image"),
    


    # --- USER MANAGEMENT (Admin Panel) ---
    path('users/', views.admin_users, name='admin_users'),
    path('users/add/', views.add_user, name='add_user'),
    path('users/block/<int:user_id>/', views.block_user, name='block_user'),
    path('users/unblock/<int:user_id>/', views.unblock_user, name='unblock_user'),
    path('api/notification/<int:id>/', NotificationDetailAPIView.as_view(), name='notification-detail'),
    path('notification/mark-read/<int:pk>/', NotificationMarkReadView.as_view(), name='notification-mark-read')
    


]