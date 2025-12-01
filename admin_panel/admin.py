from django.contrib import admin
from .models import Doctor, Appointment, DoctorAvailability, EyeScreening, Notification, UserProfile

admin.site.register(Doctor)
admin.site.register(Appointment)
admin.site.register(DoctorAvailability)
admin.site.register(EyeScreening)
admin.site.register(Notification)
admin.site.register(UserProfile)


