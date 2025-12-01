# admin_panel/utils.py

from .models import Notification, Doctor, User
from django.utils import timezone

def create_notification(user, title, message):
    """Creates a notification for a user"""
    Notification.objects.create(
        user=user,
        title=title,
        message=message,
        timestamp=timezone.now()
    )

def create_admin_notification(title, message):
    """Creates a notification for all admins"""
    doctors = Doctor.objects.all()
    for doc in doctors:
        Notification.objects.create(
            user=doc.user,
            title=title,
            message=message,
            timestamp=timezone.now()
        )
#STOP CNTRL Z



# In your app/utils.py

import random
from datetime import timedelta
from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings
from .models import OneTimePassword # Import the model from the same app

def send_otp_email(user):
    """Generates an OTP and sends it to the user's registered email."""
    try:
        otp_instance, _ = OneTimePassword.objects.get_or_create(user=user)
        
        # Generate and save a new OTP code 
        otp_instance.generate_new_otp() 

        subject = 'Your SmartSight Login Verification Code (OTP)'
        message = f"""
Dear {user.get_full_name() or user.username},

Your One-Time Password (OTP) for SmartSight login is: {otp_instance.otp_code}

This code is valid for 5 minutes. Please enter it on the login screen to proceed.

If you did not request this code, please ignore this email.

Thank you,
SmartSight Team
"""
        from_email = settings.DEFAULT_FROM_EMAIL
        recipient_list = [user.email]
        
        send_mail(subject, message, from_email, recipient_list)
        
        return True
    except Exception as e:
        print(f"Error sending OTP to {user.email}: {e}")
        return False
