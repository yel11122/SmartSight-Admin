#current model.py

from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver




from django.db import models
from django.contrib.auth.models import User

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    date_of_birth = models.DateField(null=True, blank=True)

    GENDER_CHOICES = [
        ('male', 'Male'),
        ('female', 'Female'),
    ]
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES, null=True, blank=True)

    push_token = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        help_text="Token for sending push notifications (e.g., Firebase/Expo token)."
    )

    def __str__(self):
        return f"Profile for {self.user.username}"



@receiver(post_save, sender=User)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)
    if hasattr(instance, 'userprofile'):
        instance.userprofile.save()


# --- DOCTOR ---
class Doctor(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    specialty = models.CharField(max_length=100)
    is_pediatric = models.BooleanField(default=False)
    push_token = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        help_text="Token for sending push notifications (e.g., Firebase/Expo token)"
    )

    def __str__(self):
        if self.user:
            full_name = self.user.get_full_name() or self.user.username
            return f" {full_name} ({self.specialty})"
        return f"Doctor (Unassigned) - {self.specialty}"


# --- APPOINTMENT ---
class Appointment(models.Model):
    STATUS_CHOICES = (
        ('Pending', 'Pending'),
        ('Scheduled', 'Scheduled'),
        ('Completed', 'Completed'),
        ('Cancelled', 'Cancelled'),
    )

    GENDER_CHOICES = (
        ('male', 'Male'),
        ('female', 'Female'),

    )

    BOOKING_FOR_CHOICES = (
        ('yourself', 'Yourself'),
        ('another', 'Another Person'),
    )

    REASON_CHOICES = (
        ('Internal eye examination', 'Internal eye examination'),
        ('External eye examination', 'External eye examination'),
        ('Glaucoma Screening', 'Glaucoma Screening'),
        ('Keratoconus Screening', 'Keratoconus Screening'),
        ('Vision therapy', 'Vision therapy'),
        ('Adult and pediatric comprehensive vision', 'Adult and pediatric comprehensive vision'),
        ('Examination', 'Examination'),
        ('Binocular vision exam', 'Binocular vision exam'),
        ('Color vision tests', 'Color vision tests'),
        ('Myopia management', 'Myopia management'),
        ('Dry eye test and management', 'Dry eye test and management'),
    )

    # Link appointment to user who booked
    booker = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='booked_appointments',
        verbose_name='User Who Booked'
    )

    # Patient info
    patient_first_name = models.CharField(max_length=100)
    patient_last_name = models.CharField(max_length=100)
    patient_email = models.EmailField(max_length=255, blank=True, null=True)
    patient_age = models.IntegerField(null=True, blank=True)
    patient_gender = models.CharField(max_length=10, choices=GENDER_CHOICES, default='other')
    reason = models.CharField(max_length=100, choices=REASON_CHOICES, null=True, blank=True)
    booking_for = models.CharField(max_length=20, choices=BOOKING_FOR_CHOICES, default="yourself")

    # Scheduling info
    doctor = models.ForeignKey("Doctor", on_delete=models.CASCADE, null=True, blank=True)
    appointment_datetime = models.DateTimeField()
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='Pending')
    archive = models.BooleanField(default=False)
    is_ai_screening = models.BooleanField(default=True)
    preliminary_result = models.TextField(blank=True, null=True)  # 👈 Important


    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        if self.doctor and self.doctor.user:
            doc_name = self.doctor.user.get_full_name() or self.doctor.user.username
        else:
            doc_name = "Unassigned Doctor"
        return f"Appointment with {doc_name} for {self.patient_first_name} {self.patient_last_name}"
    
   # Track original status for signals
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._original_status = self.status



# --- DOCTOR AVAILABILITY ---
class DoctorAvailability(models.Model):
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE)
    date = models.DateField()
    time_slots = models.JSONField(default=list)

    class Meta:
        unique_together = ('doctor', 'date')

    def __str__(self):
        doc = self.doctor.user.get_full_name() if (self.doctor and self.doctor.user) else "TBD"
        return f"Availability for {doc} on {self.date}"


# --- NOTIFICATION ---
class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    message = models.TextField()
    url = models.CharField(max_length=255, blank=True, null=True)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.title} for {self.user.username}"
    


class EyeScreening(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, null=True, blank=True,
        related_name='eye_screenings'
    )
    image = models.ImageField(upload_to='screening_images/')
    result = models.CharField(max_length=50)  # e.g., "Strabismus" or "Strabismus-Free"
    confidence = models.FloatField()
    remarks = models.TextField(blank=True, null=True)  # Optional AI message or notes
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username if self.user else 'Anonymous'} - {self.result} ({self.confidence:.2f})"


#CONTROL Z

 