import datetime
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.urls import reverse
from django.utils import timezone
from .models import Appointment, DoctorAvailability
from .views import create_admin_notification, create_notification


# ----------------------------------------------
# 🧑‍⚕️ ADMIN NOTIFICATIONS
# ----------------------------------------------

@receiver(post_save, sender=Appointment)
def notify_admin_on_appointment_creation(sender, instance, created, **kwargs):
    """Notify admin when a new appointment is created."""
    if created:
        try:
            url = reverse('get_patient_details', args=[instance.id])
        except:
            url = None

        # Format local time same as frontend
        local_dt = timezone.localtime(instance.appointment_datetime)
        formatted_time = local_dt.strftime("%b %d, %Y at %I:%M %p")

        create_admin_notification(
            "New Appointment Scheduled",
            f"{instance.patient_first_name} {instance.patient_last_name} booked with "
            f"{instance.doctor.user.get_full_name() if instance.doctor else 'a doctor'} on {formatted_time}.",
            url=url
        )


@receiver(pre_save, sender=Appointment)
def notify_admin_on_appointment_status_change(sender, instance, **kwargs):
    """Notify admin when an appointment’s status changes."""
    if not instance.pk:
        return  # Skip new

    try:
        old_instance = Appointment.objects.get(pk=instance.pk)
    except Appointment.DoesNotExist:
        return

    if old_instance.status != instance.status:
        create_admin_notification(
            f"Appointment {instance.status}",
            f"Appointment for {instance.patient_first_name} {instance.patient_last_name} "
            f"is now marked as **{instance.status}**."
        )


@receiver(post_save, sender=DoctorAvailability)
def notify_admin_on_doctor_availability_change(sender, instance, created, **kwargs):
    """Notify admin when doctor availability is created or updated."""
    doctor_name = instance.doctor.user.get_full_name() if instance.doctor else "Unknown Doctor"
    date_str = instance.date.strftime("%B %d, %Y")

    msg = (
        f"{doctor_name} added new availability slots for {date_str}."
        if created
        else f"{doctor_name} updated availability slots for {date_str}."
    )

    create_admin_notification("Doctor Availability Updated", msg)


# ----------------------------------------------
# 👩‍💼 USER NOTIFICATIONS
# ----------------------------------------------

@receiver(pre_save, sender=Appointment)
def notify_user_status_change(sender, instance, **kwargs):
    """Notify user when their appointment status changes."""
    if not instance.pk:
        return  # Skip new appointments (handled at creation)

    try:
        old_instance = Appointment.objects.get(pk=instance.pk)
    except Appointment.DoesNotExist:
        return

    old_status = old_instance.status
    new_status = instance.status

    if old_status != new_status and instance.booker:
        # Format date/time same as frontend (localized)
        local_dt = timezone.localtime(instance.appointment_datetime)
        formatted_date = local_dt.strftime("%B %d, %Y")
        formatted_time = local_dt.strftime("%I:%M %p")
        full_datetime_str = f"{formatted_date} {formatted_time}"

        doctor_name = (
            instance.doctor.user.get_full_name() if instance.doctor else "your doctor"
        )

        # ✅ User-friendly wording
        if new_status.lower() == "scheduled":
            create_notification(
                instance.booker,
                "Appointment Confirmed ✅ ",
                f"Your appointment with {doctor_name} on {full_datetime_str} has been confirmed."
            )
        elif new_status.lower() == "completed":
            create_notification(
                instance.booker,
                "Appointment Completed 🎉",
                f"Your appointment on {full_datetime_str} has been marked as completed. Thank you for visiting!"
            )
        elif new_status.lower() == "cancelled":
            create_notification(
                instance.booker,
                "Appointment Cancelled ❌",
                f"Your appointment on {full_datetime_str} was cancelled. You may rebook anytime."
            )
        elif new_status.lower() == "pending":
            create_notification(
                instance.booker,
                "⏳ Appointment Pending",
                f"Your appointment with {doctor_name} on {full_datetime_str} is pending confirmation."
            )
