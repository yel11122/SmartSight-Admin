#current views.py



import datetime
import json
import logging 
from datetime import timedelta

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.utils.decorators import method_decorator
from django.utils.timezone import now
from django.views.decorators.csrf import csrf_exempt

from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.authtoken.models import Token
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication
from channels.layers import get_channel_layer  #added
from asgiref.sync import async_to_sync      #added
import json        #added
#ADDED FOR DOCTORS#

# In admin_panel/views.py

from django.shortcuts import render
from django.contrib.auth.decorators import login_required




from .models import Appointment, Doctor, DoctorAvailability, Notification
from .serializers import (
    RegisterSerializer,
    DoctorAvailabilitySerializer,
    DoctorSerializer,
    AppointmentSerializer,
)


# ---------- NOTIFICATION HELPERS ----------
def create_notification(user, title, message, url=None):
    Notification.objects.create(user=user, title=title, message=message, url=url)

def create_admin_notification(title, message, url=None):
    admins = User.objects.filter(is_staff=True)
    for admin in admins:
        create_notification(admin, title, message, url)


# ---------------------------
# ADMIN PANEL VIEWS (No Changes)
# ---------------------------

@login_required
def admin_home(request):
    """Admin dashboard view displaying key metrics."""
    total_appointments = Appointment.objects.count()
    pending_appointments = Appointment.objects.filter(status="Pending").count()
    active_doctors = Doctor.objects.count()
    return render(
        request,
        "admin_panel/home.html",
        {
            "total_appointments": total_appointments,
            "pending_appointments": pending_appointments,
            "active_doctors": active_doctors,
        },
    )


def admin_login(request):
    """Admin login view, restricting access to staff users."""
    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")
        try:
            user = User.objects.get(email__iexact=email)
            if not user.is_staff:
                return render(
                    request,
                    "admin_panel/login.html",
                    {"error": "Only staff can access admin panel."},
                )

            authenticated_user = authenticate(
                request, username=user.username, password=password
            )
            if authenticated_user:
                login(request, authenticated_user)
                return redirect("admin_home")
            else:
                return render(
                    request,
                    "admin_panel/login.html",
                    {"error": "Invalid credentials."},
                )
        except User.DoesNotExist:
            return render(
                request,
                "admin_panel/login.html",
                {"error": "User does not exist."},
            )
    return render(request, "admin_panel/login.html")


def admin_logout(request):
    """Logs out the admin user and redirects to the login page."""
    logout(request)
    return redirect("admin_login")


def admin_register(request):
    """Registers a new staff user for the admin panel."""
    if request.method == "POST":
        email = request.POST.get("email")
        username = request.POST.get("username")
        password = request.POST.get("password")

        if User.objects.filter(email=email).exists():
            return render(
                request,
                "admin_panel/register.html",
                {"error": "Email already registered."},
            )
        if User.objects.filter(username=username).exists():
            return render(
                request,
                "admin_panel/register.html",
                {"error": "Username already taken."},
            )

        User.objects.create_user(username=username, email=email, password=password, is_staff=True)
        return redirect("admin_login")
    return render(request, "admin_panel/register.html")

#ADDED FOR DOCTORS#

import datetime
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.utils import timezone

# --- DRF and API Imports ---
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from django.http import JsonResponse
# Assuming these models and serializers exist in your app structure
# Replace these imports with your actual model and serializer paths
from .models import Notification # Placeholder import
from .serializers import NotificationSerializer # Placeholder import


# =======================================================
# WEB ADMIN PANEL VIEWS (Excerpts for context)
# =======================================================

@login_required
def manage_doctors_hub_view(request):
    """Renders the Doctor Management Hub (manage_doctors.html)."""
    return render(request, 'admin_panel/manage_doctors.html')


@login_required
def add_doctor(request):
    """
    Renders the form to add a new doctor (add_doctor_form.html).
    """
    context = {
        'page_title': 'Add New Doctor Profile',
    }
    return render(request, 'admin_panel/add_doctor_form.html', context)
    
# ... (Other Web Views like admin_login, monitor_appointments, etc.)

# =======================================================
# API ENDPOINTS (DRF Views)
# =======================================================

# --- NOTIFICATION API VIEWS (Added as requested) ---

class NotificationDetailAPIView(generics.RetrieveAPIView):
    """API endpoint to retrieve a single notification by ID."""
    # Placeholder: Use your actual Notification model
    queryset = Notification.objects.all() 
    # Placeholder: Use your actual Notification Serializer
    serializer_class = NotificationSerializer 
    permission_classes = [IsAuthenticated]
    lookup_field = 'id' # Matches the <int:id> in the API URL path


class MarkNotificationReadAPIView(generics.UpdateAPIView):
    """
    API endpoint to mark a specific notification as read using a PATCH/PUT request.
    This is often linked to the /api/notification/<int:pk>/read/ path.
    """
    # Placeholder: Use your actual Notification model
    queryset = Notification.objects.all() 
    # Placeholder: Use your actual Notification Serializer (optional, can be omitted if not returning data)
    serializer_class = NotificationSerializer 
    permission_classes = [IsAuthenticated]
    http_method_names = ['patch']
    
    def update(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            # Check ownership/permissions here if necessary
            
            instance.is_read = True
            instance.read_at = timezone.now()
            instance.save(update_fields=['is_read', 'read_at'])
            return Response({'status': 'Notification marked as read'}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


class NotificationMarkReadView(APIView):
    """
    A custom APIView designed for marking a notification as read, possibly 
    used for an alternative or administrative path.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        try:
            # Placeholder: Use your actual Notification model
            notification = Notification.objects.get(pk=pk) 
            
            # Check ownership/permissions here if necessary
            
            notification.is_read = True
            notification.read_at = timezone.now()
            notification.save(update_fields=['is_read', 'read_at'])
            return Response({'status': f'Notification {pk} marked as read'}, status=status.HTTP_200_OK)
        except Notification.DoesNotExist:
            return Response({'error': 'Notification not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

# ... (Other API Views like RegisterView, LoginUserAPIView, etc.)


@login_required
@require_POST
def archive_appointment(request):
    """Archives a single appointment via a POST request."""
    appointment_id = request.POST.get("id")
    appointment = get_object_or_404(Appointment, pk=appointment_id)
    appointment.archive = True
    appointment.save()
    return JsonResponse({"success": True, "message": "Appointment archived."})


@login_required
def admin_profile(request):
    """Displays the admin user's profile information."""
    return render(request, "admin_panel/profile.html", {"user": request.user})


@login_required
def manage_doctors_availability(request):
    """Manages and displays doctor availability for a selected date."""
    doctor_id = request.GET.get('doctor_id')
    date_str = request.GET.get('date')

    if doctor_id and date_str:
        try:
            # Parse date string safely
            try:
                date_obj = datetime.datetime.strptime(date_str, "%Y-%m-%d").date()
            except ValueError:
                return JsonResponse({"error": "Invalid date format. Use YYYY-MM-DD."}, status=400)

            doctor = get_object_or_404(Doctor, id=doctor_id)

            occupied_qs = Appointment.objects.filter(
                doctor=doctor,
                status="Scheduled",
                appointment_datetime__date=date_obj
            ).order_by('appointment_datetime')

            occupied_slots = []
            for app in occupied_qs:
                start = app.appointment_datetime
                end = start + datetime.timedelta(minutes=30)
                occupied_slots.append(f"{start.strftime('%I:%M %p')} - {end.strftime('%I:%M %p')}")

            availability, _ = DoctorAvailability.objects.get_or_create(
                doctor=doctor,
                date=date_obj
            )
            vacant_slots = availability.time_slots or []

            return JsonResponse({
                "occupied_slots": occupied_slots,
                "vacant_slots": vacant_slots,
            })
        except Exception as e:
            logging.getLogger(__name__).error(f"Error in manage_doctors_availability: {str(e)}")
            return JsonResponse({'error': str(e)}, status=500)

    doctors = Doctor.objects.all()
    return render(
        request,
        "admin_panel/manage_doctors_availability.html",
        {"doctors": doctors},
    )


@login_required
@require_POST
def set_doctor_availability(request):
    """Sets or updates a doctor's available time slots for a specific date."""
    try:
        doctor_id = request.POST.get("doctor_id")
        date_str = request.POST.get("date")
        time_slots_str = request.POST.get("time_slots")

        if not all([doctor_id, date_str, time_slots_str]):
            return JsonResponse({"success": False, "error": "Missing required data."}, status=400)

        doctor = get_object_or_404(Doctor, pk=doctor_id)
        time_slots_list = json.loads(time_slots_str)

        DoctorAvailability.objects.update_or_create(
            doctor=doctor,
            date=date_str,
            defaults={'time_slots': time_slots_list}
        )
        return JsonResponse({"success": True, "message": "Availability updated successfully."})

    except json.JSONDecodeError:
        return JsonResponse({"success": False, "error": "Invalid time slots data."}, status=400)
    except Exception as e:
        return JsonResponse({"success": False, "error": str(e)}, status=500)


from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from .models import Appointment

@login_required
def doctor_overview_patients_record(request):
    """
    Displays a list of non-archived patient appointments
    that are only in 'Scheduled' status.
    """
    patients = Appointment.objects.filter(
        archive=False,
        status="Scheduled"  # ✅ Only scheduled appointments
    ).order_by("patient_last_name")

    return render(
        request,
        "admin_panel/doctor_overview_patients_record.html",
        {"patients": patients},
    )



@login_required
@require_POST
def archive_patient(request):
    """Archives a patient record."""
    patient = get_object_or_404(Appointment, pk=request.POST.get("id"))
    patient.archive = True
    patient.save()
    return JsonResponse({"success": True, "message": "Patient record archived."})


@login_required
def add_appointment(request):
    """Allows an admin to manually add a new appointment."""
    if request.method == "POST":
        doctor = get_object_or_404(Doctor, pk=request.POST.get("doctor_id"))
        appointment_datetime = datetime.datetime.fromisoformat(request.POST.get("appointment_datetime"))
        Appointment.objects.create(
            patient_first_name=request.POST.get("patient_first_name"),
            patient_last_name=request.POST.get("patient_last_name"),
            patient_age=request.POST.get("patient_age") or None,
            patient_gender=request.POST.get("patient_gender") or "other",
            reason=request.POST.get("reason") or "",
            booking_for=request.POST.get("booking_for") or "yourself",
            
            status=request.POST.get("status") or "Scheduled",
            appointment_datetime=appointment_datetime,
            doctor=doctor,
        )
        return redirect("monitor_appointments")

    doctors = Doctor.objects.all()
    return render(request, "admin_panel/add_appointment.html", {"doctors": doctors})



import datetime
import json
import logging
from datetime import timedelta

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.authtoken.models import Token
from rest_framework.permissions import AllowAny

from .models import Appointment, Doctor, DoctorAvailability, Notification
from .serializers import RegisterSerializer, DoctorAvailabilitySerializer, DoctorSerializer, AppointmentSerializer


# ---------------------------
# NOTIFICATION HELPERS
# ---------------------------
def create_notification(user, title, message, url=None):
    Notification.objects.create(user=user, title=title, message=message, url=url)


def create_admin_notification(title, message, url=None):
    admins = User.objects.filter(is_staff=True)
    for admin in admins:
        create_notification(admin, title, message, url)


# ---------------------------
# ADMIN PANEL VIEWS
# ---------------------------
@login_required
def admin_home(request):
    total_appointments = Appointment.objects.count()
    pending_appointments = Appointment.objects.filter(status="Pending").count()
    active_doctors = Doctor.objects.count()
    return render(
        request,
        "admin_panel/home.html",
        {
            "total_appointments": total_appointments,
            "pending_appointments": pending_appointments,
            "active_doctors": active_doctors,
        },
    )


def admin_login(request):
    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")
        try:
            user = User.objects.get(email__iexact=email)
            if not user.is_staff:
                return render(request, "admin_panel/login.html", {"error": "Only staff can access admin panel."})

            authenticated_user = authenticate(request, username=user.username, password=password)
            if authenticated_user:
                login(request, authenticated_user)
                return redirect("admin_home")
            else:
                return render(request, "admin_panel/login.html", {"error": "Invalid credentials."})
        except User.DoesNotExist:
            return render(request, "admin_panel/login.html", {"error": "User does not exist."})
    return render(request, "admin_panel/login.html")


def admin_logout(request):
    logout(request)
    return redirect("admin_login")


def admin_register(request):
    if request.method == "POST":
        email = request.POST.get("email")
        username = request.POST.get("username")
        password = request.POST.get("password")

        if User.objects.filter(email=email).exists():
            return render(request, "admin_panel/register.html", {"error": "Email already registered."})
        if User.objects.filter(username=username).exists():
            return render(request, "admin_panel/register.html", {"error": "Username already taken."})

        User.objects.create_user(username=username, email=email, password=password, is_staff=True)
        return redirect("admin_login")
    return render(request, "admin_panel/register.html")


from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from itertools import groupby
from django.utils.timezone import localtime
from .models import Appointment

@login_required
def monitor_appointments(request):
    """
    Displays appointments grouped by date with AI filter support.
    filter_type = 'with_ai', 'without_ai', or 'all'
    """
    filter_type = request.GET.get('filter', 'all')  # default to 'all'

    if filter_type == 'with_ai':
        appointments = Appointment.objects.filter(archive=False, is_ai_screening=True).order_by("appointment_datetime")
    elif filter_type == 'without_ai':
        appointments = Appointment.objects.filter(archive=False, is_ai_screening=False).order_by("appointment_datetime")
    else:
        # Show all appointments (both AI and standard)
        appointments = Appointment.objects.filter(archive=False).order_by("appointment_datetime")

    # Group appointments by date
    grouped_appointments = {}
    for date, group in groupby(appointments, key=lambda a: localtime(a.appointment_datetime).date()):
        grouped_appointments[date] = list(group)

    context = {
        'grouped_appointments': grouped_appointments,
        'filter_type': filter_type
    }
    return render(request, "admin_panel/appointments.html", context)



@login_required
@require_POST
def archive_appointment(request):
    appointment_id = request.POST.get("id")
    appointment = get_object_or_404(Appointment, pk=appointment_id)
    appointment.archive = True
    appointment.save()
    return JsonResponse({"success": True, "message": "Appointment archived."})


@login_required
def admin_profile(request):
    return render(request, "admin_panel/profile.html", {"user": request.user})


@login_required
def manage_doctors_availability(request):
    doctor_id = request.GET.get('doctor_id')
    date_str = request.GET.get('date')

    if doctor_id and date_str:
        try:
            date_obj = datetime.datetime.strptime(date_str, "%Y-%m-%d").date()
            doctor = get_object_or_404(Doctor, id=doctor_id)

            occupied_qs = Appointment.objects.filter(
                doctor=doctor,
                status="Scheduled",
                appointment_datetime__date=date_obj
            ).order_by('appointment_datetime')

            occupied_slots = [
                f"{app.appointment_datetime.strftime('%I:%M %p')} - {(app.appointment_datetime + timedelta(minutes=30)).strftime('%I:%M %p')}"
                for app in occupied_qs
            ]

            availability, _ = DoctorAvailability.objects.get_or_create(doctor=doctor, date=date_obj)
            vacant_slots = availability.time_slots or []

            return JsonResponse({"occupied_slots": occupied_slots, "vacant_slots": vacant_slots})

        except Exception as e:
            logging.error(f"Error in manage_doctors_availability: {str(e)}")
            return JsonResponse({'error': str(e)}, status=500)

    doctors = Doctor.objects.all()
    return render(request, "admin_panel/manage_doctors_availability.html", {"doctors": doctors})


@login_required
@require_POST
def set_doctor_availability(request):
    try:
        doctor_id = request.POST.get("doctor_id")
        date_str = request.POST.get("date")
        time_slots_str = request.POST.get("time_slots")

        if not all([doctor_id, date_str, time_slots_str]):
            return JsonResponse({"success": False, "error": "Missing required data."}, status=400)

        doctor = get_object_or_404(Doctor, pk=doctor_id)
        time_slots_list = json.loads(time_slots_str)

        DoctorAvailability.objects.update_or_create(
            doctor=doctor,
            date=date_str,
            defaults={'time_slots': time_slots_list}
        )
        return JsonResponse({"success": True, "message": "Availability updated successfully."})

    except json.JSONDecodeError:
        return JsonResponse({"success": False, "error": "Invalid time slots data."}, status=400)
    except Exception as e:
        return JsonResponse({"success": False, "error": str(e)}, status=500)



@login_required
@require_POST
def archive_patient(request):
    patient = get_object_or_404(Appointment, pk=request.POST.get("id"))
    patient.archive = True
    patient.save()
    return JsonResponse({"success": True, "message": "Patient record archived."})


@login_required
def add_appointment(request):
    if request.method == "POST":
        doctor = get_object_or_404(Doctor, pk=request.POST.get("doctor_id"))
        appointment_datetime = datetime.datetime.fromisoformat(request.POST.get("appointment_datetime"))
        Appointment.objects.create(
            patient_first_name=request.POST.get("patient_first_name"),
            patient_last_name=request.POST.get("patient_last_name"),
            patient_age=request.POST.get("patient_age") or None,
            patient_gender=request.POST.get("patient_gender") or "other",
            reason=request.POST.get("reason") or "",
            booking_for=request.POST.get("booking_for") or "yourself",
          
            status=request.POST.get("status") or "Scheduled",
            appointment_datetime=appointment_datetime,
            doctor=doctor,
        )
        return redirect("monitor_appointments")

    doctors = Doctor.objects.all()
    return render(request, "admin_panel/add_appointment.html", {"doctors": doctors})

# ---------------------------
# API VIEWS FOR MOBILE APP
# ---------------------------

from .models import UserProfile, Doctor, Appointment

# Updated RegisterView in views.py

@method_decorator(csrf_exempt, name='dispatch')
class RegisterView(APIView):
    permission_classes = [AllowAny]
    authentication_classes = []

    def post(self, request):
        print("📥 Incoming data:", request.data)
        serializer = RegisterSerializer(data=request.data)

        if serializer.is_valid():
            user = serializer.save()
            token, _ = Token.objects.get_or_create(user=user)

            # ✅ FIX: Retrieve UserProfile object
            try:
                user_profile = UserProfile.objects.get(user=user)
            except UserProfile.DoesNotExist:
                # Should not happen if serializer.create ran correctly, but good practice
                user_profile = None 

            # Optional notification creation (assuming helper functions are defined)
            # try:
            #     create_admin_notification(...)
            #     create_notification(...)
            # except Exception as e:
            #     print("⚠️ Notification error:", e)

           # Optional notification creation
            try:
                create_admin_notification(
                    "New User Registered",
                    f"A new user, {user.get_full_name() or user.username}, has just registered."
                )
                create_notification(
                    user,
                    "Registration Successful",
                    "Welcome to SmartSight! Your account has been created successfully."
                )
            except Exception as e:
                print("⚠️ Notification error:", e)

            # Include gender and date_of_birth in response
            return Response({
                "message": "User registered successfully",
                "user": {
                    "id": user.id,
                    "first_name": user.first_name,
                    "last_name": user.last_name,
                    "email": user.email,
                    "gender": getattr(user, "gender", None),
                    "date_of_birth": getattr(user, "date_of_birth", None),
                },
                "token": token.key
            }, status=status.HTTP_201_CREATED)

        print("❌ Validation errors:", serializer.errors)
        return Response({"errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

        

# Updated LoginUserAPIView in views.py

@method_decorator(csrf_exempt, name='dispatch')
class LoginUserAPIView(APIView):
    permission_classes = [AllowAny]
    authentication_classes = []

    def post(self, request):
        username_or_email = request.data.get("username")
        password = request.data.get("password")
        # ... (rest of the validation checks remain the same) ...

        try:
            user = User.objects.get(email__iexact=username_or_email)
            # ... (Staff/Blocked checks) ...

            if not user.check_password(password):
                return Response({"message": "Invalid credentials."}, status=status.HTTP_401_UNAUTHORIZED)
            
            # ✅ FIX: Get UserProfile data
            try:
                user_profile = UserProfile.objects.get(user=user)
                dob = user_profile.date_of_birth
                gender = user_profile.gender
            except UserProfile.DoesNotExist:
                dob = None
                gender = None
            
        except User.DoesNotExist:
            return Response({"message": "Invalid credentials."}, status=status.HTTP_401_UNAUTHORIZED)
        except Exception as e:
            return Response({"message": f"Server error: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        # ✅ SUCCESS Response
        token, _ = Token.objects.get_or_create(user=user)
        return Response({
            "message": "Login successful.",
            "name": user.username,
            "email": user.email,
            "first_name": user.first_name,
            "last_name": user.last_name,
            
            # ✅ NEW: Include profile fields for client to save
            "date_of_birth": dob,
            "gender": gender,
            # Note: profile_image is assumed to be handled elsewhere (e.g., Doctor/UserProfile model)
            # You might need to add: "profile_image": user_profile.profile_image.url if user_profile and user_profile.profile_image else None
            
            "token": token.key
        })

class RegisterPushTokenAPIView(APIView):
    """
    API endpoint to register or update the user's push notification token.
    Saves the token to the Doctor profile associated with the authenticated user.
    """
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        
        # --- CRITICAL DIAGNOSTIC LOG START ---
        logger = logging.getLogger(__name__)
        logger.error(f"DEBUG AUTH: Push Token Request received from User ID: {request.user.id}, Email: {request.user.email}")
        # --- CRITICAL DIAGNOSTIC LOG END ---
        
        push_token = request.data.get('push_token') 

        if not push_token:
            return Response({"success": False, "error": "Missing 'push_token' in request body."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Assuming the authenticated user is linked to a Doctor model
            # Note: This means this endpoint is only for doctors, not patients.
            doctor_profile = Doctor.objects.get(user=request.user)
            
            # NOTE: The Doctor model MUST have a 'push_token' field defined. 
            doctor_profile.push_token = push_token 
            doctor_profile.save()
            
            return Response({
                "success": True, 
                "message": "Push token registered successfully for doctor."
            }, status=status.HTTP_200_OK)

        except Doctor.DoesNotExist:
            # Handle cases where the authenticated user is a patient/admin, not a doctor
            return Response({
                "success": False, 
                "error": "User is authenticated but no associated Doctor profile was found to save the token."
            }, status=status.HTTP_404_NOT_FOUND)
        
        except Exception as e:
            # Catch other potential errors, like if push_token field doesn't exist on Doctor
            return Response({
                "success": False, 
                "error": f"Failed to save token: {str(e)}"
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class UpdateProfileAPIView(APIView):
    """
    API endpoint for authenticated users to update their profile.
    Handles the POST request sent by the mobile app for profile updates.
    """
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        user = request.user
        data = request.data

        user.first_name = data.get('first_name', user.first_name)
        user.last_name = data.get('last_name', user.last_name)
        user.email = data.get('email', user.email).lower()
        user.username = user.email

        # ✅ Handle custom fields
        profile = user.profile  # assuming you have a OneToOneField to Profile model
        profile.date_of_birth = data.get('date_of_birth', profile.date_of_birth)
        profile.age = data.get('age', profile.age)
        profile.gender = data.get('gender', profile.gender)
        profile.save()
        user.save()

        return Response({
            "message": "Profile updated successfully.",
            "first_name": user.first_name,
            "last_name": user.last_name,
            "email": user.email,
            "date_of_birth": profile.date_of_birth,
            "age": profile.age,
            "gender": profile.gender,
        }, status=status.HTTP_200_OK)

    """
    API endpoint for authenticated users to update their profile.
    Handles the POST request sent by the mobile app for profile updates.
    """
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    # Renamed the method from 'put' to 'post' to match the client's request
    def post(self, request, *args, **kwargs):
        user = request.user
        data = request.data
        
        # Update user fields
        user.first_name = data.get('first_name', user.first_name)
        user.last_name = data.get('last_name', user.last_name)
        
        # Handle email change and username
        new_email = data.get('email', user.email).lower()
        if new_email and new_email != user.email:
            # Check if new email is already taken by another user
            if User.objects.filter(email__iexact=new_email).exclude(pk=user.pk).exists():
                return Response({"error": "This email is already in use by another account."}, status=status.HTTP_400_BAD_REQUEST)
            user.email = new_email
            user.username = new_email # Assuming username is tied to email
        
        try:
            # Check if the user has an associated Doctor profile and update those fields
            if hasattr(user, 'doctor'):
                user.doctor.phone = data.get('phone', user.doctor.phone)
                user.doctor.address = data.get('address', user.doctor.address)
                # Note: Handling file uploads (profile_image) is more complex and usually requires a Serializer or custom handling.
                # user.doctor.profile_image = data.get('profile_image', user.doctor.profile_image)
                user.doctor.save()
            else:
                # This path is hit if the user is a standard patient without a Doctor profile
                pass 
        except Exception as e:
            # Log unexpected database/model errors
            logging.getLogger(__name__).error(f"Error updating related profile data for user {user.id}: {str(e)}")
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        user.save()
        
        # Prepare response data, being careful not to crash if there's no doctor profile
        phone = user.doctor.phone if hasattr(user, 'doctor') else None
        address = user.doctor.address if hasattr(user, 'doctor') else None
        profile_image = user.doctor.profile_image if hasattr(user, 'doctor') else None
        
        return Response({
            "message": "Profile updated successfully.",
            "first_name": user.first_name,
            "last_name": user.last_name,
            "email": user.email,
            "phone": phone,
            "address": address,
            "profile_image": profile_image,
        }, status=status.HTTP_200_OK)


class DoctorListAPIView(generics.ListAPIView):
    """API endpoint to list all doctors."""
    queryset = Doctor.objects.all()
    serializer_class = DoctorSerializer


class DoctorAvailabilityAPIView(generics.ListAPIView):
    """API endpoint to list doctor availability, with optional filtering by doctor and date."""
    serializer_class = DoctorAvailabilitySerializer

    def get_queryset(self):
        doctor_id = self.request.query_params.get('doctor_id')
        date = self.request.query_params.get('date')
        qs = DoctorAvailability.objects.all()
        if doctor_id:
            qs = qs.filter(doctor_id=doctor_id)
        if date:
            qs = qs.filter(date=date)
        return qs

from django.db.models import F

class AssignedDoctorAvailabilityAPIView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        age = request.query_params.get('age')
        date_str = request.query_params.get('date')

        try:
            age = int(age)
        except (TypeError, ValueError):
            return Response({"success": False, "error": "Invalid or missing 'age' param"}, status=400)

        # Assign doctor based on age
        if age < 18:
            doctor = Doctor.objects.filter(is_pediatric=True).first()
        else:
            doctor = Doctor.objects.filter(is_pediatric=False).first()

        if not doctor:
            return Response({"success": False, "error": "No doctor found for this age"}, status=404)

        today = datetime.date.today()
        available_dates_qs = DoctorAvailability.objects.filter(doctor=doctor, date__gte=today).order_by('date')
        available_dates = [avail.date.isoformat() for avail in available_dates_qs if avail.time_slots]

        availability = None
        if date_str:
            availability = available_dates_qs.filter(date=date_str).first()
        elif available_dates:
            availability = available_dates_qs.first()

        slots = availability.time_slots if availability else []

        # Filter out already booked slots
        if availability:
            booked_appointments = Appointment.objects.filter(
                doctor=doctor,
                appointment_datetime__date=availability.date
            ).values_list('appointment_datetime__time', flat=True)

            # convert time to the same string format as your time_slots
            booked_time_strs = [appt.strftime("%I:%M %p") for appt in booked_appointments]
            slots = [slot for slot in slots if slot not in booked_time_strs]

        serializer = DoctorSerializer(doctor)
        return Response({
            "success": True,
            "doctor": serializer.data,
            "available_dates": available_dates,
            "selected_date": availability.date.isoformat() if availability else None,
            "time_slots": slots
        })

class AppointmentReasonsAPIView(APIView):
    """
    API endpoint to list all valid reasons for an appointment.
    """
    permission_classes = [AllowAny]  # allow access without authentication

    def get(self, request):
        reasons = [choice[0] for choice in Appointment.REASON_CHOICES]
        return Response(reasons, status=status.HTTP_200_OK)


class AppointmentGenderChoicesAPIView(APIView):
    """
    API endpoint to list valid gender choices for appointments.
    """
    permission_classes = [AllowAny]  # allow access without authentication

    def get(self, request, *args, **kwargs):
        gender_choices = [choice[0] for choice in Appointment.GENDER_CHOICES]
        return Response(gender_choices, status=status.HTTP_200_OK)


class AppointmentBookingForChoicesAPIView(APIView):
    """
    API endpoint to list valid 'booking_for' choices for appointments.
    """
    permission_classes = [AllowAny]  # allow access without authentication

    def get(self, request, *args, **kwargs):
        booking_for_choices = [choice[0] for choice in Appointment.BOOKING_FOR_CHOICES]
        return Response(booking_for_choices, status=status.HTTP_200_OK)


from django.utils import timezone
@method_decorator(csrf_exempt, name='dispatch')
class CreateAppointmentAPIView(APIView):
    permission_classes = []

    def post(self, request):
        serializer = AppointmentSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({"success": False, "errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

        try:
            if request.user.is_authenticated:
                serializer.validated_data["booker"] = request.user

                if not serializer.validated_data.get("patient_email"):
                    serializer.validated_data["patient_email"] = request.user.email
                    

                # ✅ Booking limit per day
                today = timezone.localdate()
                booking_for = serializer.validated_data.get("booking_for")
                total_booked_today = Appointment.objects.filter(booker=request.user, created_at__date=today).count()
                yourself_booked_today = Appointment.objects.filter(booker=request.user, booking_for='yourself', created_at__date=today).count()
                another_booked_today = Appointment.objects.filter(booker=request.user, booking_for='another', created_at__date=today).count()

                if total_booked_today >= 2:
                    return Response({"success": False, "error": "You can only make 2 appointments per day — 1 for yourself and 1 for another."}, status=status.HTTP_400_BAD_REQUEST)

                if booking_for == "yourself" and yourself_booked_today >= 1:
                    return Response({"success": False, "error": "You already made an appointment for yourself today."}, status=status.HTTP_400_BAD_REQUEST)

                if booking_for == "another" and another_booked_today >= 1:
                    return Response({"success": False, "error": "You already made an appointment for another person today."}, status=status.HTTP_400_BAD_REQUEST)

             # Detect AI screening
            is_ai_screening = request.data.get("is_ai_screening", False)
            serializer.validated_data["is_ai_screening"] = bool(is_ai_screening)

            # Save preliminary result if AI
            serializer.validated_data["preliminary_result"] = request.data.get("preliminary_result") if is_ai_screening else None

            # Auto-assign doctor based on age
            patient_age = serializer.validated_data.get("patient_age")
            doctor = None
            if patient_age is not None:
                doctor = Doctor.objects.filter(is_pediatric=True if patient_age < 18 else False).first()
                if doctor:
                    serializer.validated_data["doctor"] = doctor

            serializer.validated_data["status"] = "Pending"
            appt = serializer.save()

            # ✅ Auto-assign doctor based on age
            patient_age = serializer.validated_data.get("patient_age")
            doctor = None
            if patient_age is not None:
                doctor = Doctor.objects.filter(is_pediatric=True if patient_age < 18 else False).first()
                if doctor:
                    serializer.validated_data["doctor"] = doctor

            serializer.validated_data["status"] = "Pending"
            appt = serializer.save()

            local_dt = timezone.localtime(appt.appointment_datetime)
            formatted_date = local_dt.strftime("%B %d, %Y")
            formatted_time = local_dt.strftime("%I:%M %p")
            full_datetime_str = f"{formatted_date} {formatted_time}"

            # --- Notifications ---
            create_admin_notification(
                "New Appointment",
                f"{appt.patient_first_name} {appt.patient_last_name} booked an appointment "
                f"{'with AI Screening' if is_ai_screening else ''} with "
                f"{doctor.user.get_full_name() if doctor else 'a doctor'}."
            )

            if appt.booker:
                create_notification(
                    appt.booker,
                    "Appointment Pending ⏳",
                    f"Your {'AI Screening ' if is_ai_screening else ''}appointment with {doctor.user.get_full_name() if doctor else 'a doctor'} "
                    f"on {full_datetime_str} is pending confirmation."
                )

            return Response({
                "success": True,
                "message": "AI Screening appointment created successfully!" if is_ai_screening else "Appointment created successfully!",
                "id": appt.id,
                "assigned_doctor": doctor.user.get_full_name() if doctor else None,
                "is_ai_screening": is_ai_screening,
                "preliminary_result": appt.preliminary_result
            }, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response({"success": False, "error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



        

class MyAppointmentsAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # Only fetch appointments for logged-in user
        appointments = Appointment.objects.filter(booker=request.user).order_by('-appointment_datetime')
        serializer = AppointmentSerializer(appointments, many=True)
        return Response(serializer.data)



class CancelAppointmentAPIView(generics.UpdateAPIView):
    queryset = Appointment.objects.all()
    serializer_class = AppointmentSerializer
    permission_classes = [IsAuthenticated]

    def patch(self, request, *args, **kwargs):
        appointment = self.get_object()
        appointment.status = "Cancelled"
        appointment.save()

        # Notifications
        create_admin_notification(
            "Appointment Cancelled",
            f"{appointment.patient_first_name} {appointment.patient_last_name} cancelled their booking with "
            f" {appointment.doctor.user.get_full_name() if appointment.doctor else 'a doctor'}."
        )

        

        return Response({"success": True, "message": "Appointment cancelled."}, status=status.HTTP_200_OK)


class EditAppointmentAPIView(generics.UpdateAPIView):
    queryset = Appointment.objects.all()
    serializer_class = AppointmentSerializer
    permission_classes = [IsAuthenticated]

    def patch(self, request, *args, **kwargs):
        appointment = self.get_object()
        serializer = self.get_serializer(appointment, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)



class DeleteAppointmentAPIView(generics.DestroyAPIView):
    queryset = Appointment.objects.all()
    serializer_class = AppointmentSerializer
    permission_classes = [IsAuthenticated]


# --- NOTIFICATIONS API (for Mobile App) ---
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .models import Notification
from .serializers import NotificationSerializer

class NotificationListAPIView(APIView):
    """
    Returns a list of notifications for the currently authenticated user.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # Fetch notifications belonging to the logged-in user
        notifications = Notification.objects.filter(user=request.user).order_by('-created_at')
        serializer = NotificationSerializer(notifications, many=True)
        return Response(serializer.data)

class MarkNotificationReadAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        try:
            notif = Notification.objects.get(pk=pk, user=request.user)
            notif.is_read = True
            notif.save()
            return Response({"message": "Notification marked as read"})
        except Notification.DoesNotExist:
            return Response({"error": "Notification not found"}, status=404)


# ---------- ADMIN VIEWS ----------
@login_required
def get_patient_details(request, patient_id):
    appointment = get_object_or_404(Appointment, pk=patient_id)

    # Ensure datetime is converted to local timezone before formatting
    local_dt = timezone.localtime(appointment.appointment_datetime)

    data = {
        "first_name": appointment.patient_first_name,
        "last_name": appointment.patient_last_name,
        "email": appointment.patient_email if hasattr(appointment, "patient_email") else "No email provided",
        "age": appointment.patient_age,
        "gender": appointment.patient_gender,
        "reason": appointment.reason,
        "booking_for": appointment.booking_for,
        "doctor": appointment.doctor.user.get_full_name() if appointment.doctor and appointment.doctor.user else "TBD",
        "appointment_datetime": local_dt.strftime("%B %d, %Y %I:%M %p"),  # ✅ Local timezone & proper format
        "status": appointment.status,
    }

    return JsonResponse(data)


@login_required
def admin_dashboard_view(request):
    total_appointments = Appointment.objects.count()
    pending_appointments = Appointment.objects.filter(status='Pending').count()
    active_doctors = Doctor.objects.count()

    recent_activities = Appointment.objects.filter(
        created_at__gte=now() - timedelta(days=7)
    ).order_by('-created_at')[:10]

    context = {
        'total_appointments': total_appointments,
        'pending_appointments': pending_appointments,
        'active_doctors': active_doctors,
        'recent_activities': recent_activities,
    }
    return render(request, 'admin_panel/dashboard.html', context)


@login_required
def admin_users(request):
    users = User.objects.all().order_by('-date_joined')
    return render(request, "admin_panel/users.html", {"users": users})


@login_required
def add_user(request):
    if request.method == "POST":
        username = request.POST.get("username")
        email = request.POST.get("email")
        password = request.POST.get("password")
        is_staff = request.POST.get("is_staff") == "on"

        if User.objects.filter(username=username).exists():
            return render(request, "admin_panel/add_user.html", {"error": "Username already exists."})

        User.objects.create_user(username=username, email=email, password=password, is_staff=is_staff)
        return redirect("admin_users")

    return render(request, "admin_panel/add_user.html")


@login_required
def edit_user(request, user_id):
    user = get_object_or_404(User, pk=user_id)
    if request.method == "POST":
        user.username = request.POST.get("username")
        user.email = request.POST.get("email")
        user.is_staff = request.POST.get("is_staff") == "on"

        if request.POST.get("password"):
            user.set_password(request.POST.get("password"))

        user.save()
        return redirect("admin_users")

    return render(request, "admin_panel/edit_user.html", {"user": user})


@login_required
def delete_user(request, user_id):
    user = get_object_or_404(User, pk=user_id)
    if request.method == "POST":
        user.delete()
        return redirect("admin_users")

    return render(request, "admin_panel/delete_user_confirm.html", {"user": user})


@login_required
@require_POST
def archive_appointment(request):
    """Archives a single appointment via POST."""
    appointment_id = request.POST.get("id")
    appointment = get_object_or_404(Appointment, pk=appointment_id)
    appointment.archive = True
    appointment.save()
    return JsonResponse({"success": True, "message": "Appointment archived."})

@login_required
@require_POST
def archive_appointment(request):
    """Archives a single appointment via POST."""
    appointment_id = request.POST.get("id")
    appointment = get_object_or_404(Appointment, pk=appointment_id)
    appointment.archive = True
    appointment.save()
    return JsonResponse({"success": True, "message": "Appointment archived."})

@login_required
def block_user(request, user_id):
    user = get_object_or_404(User, pk=user_id)
    user.is_active = False
    user.save()
    return redirect("admin_users")


@login_required
def unblock_user(request, user_id):
    user = get_object_or_404(User, pk=user_id)
    user.is_active = True
    user.save()
    return redirect("admin_users")


# ---------- ADMIN NOTIFICATION VIEWS ----------
@login_required
def admin_notifications(request):
    notifications = Notification.objects.filter(user=request.user).order_by('-created_at')
    unread_count = notifications.filter(is_read=False).count()
    return render(request, "admin_panel/notifications.html", {"notifications": notifications, "unread_count": unread_count})


@login_required
def mark_all_notifications_read(request):
    if request.method == "POST":
        Notification.objects.filter(user=request.user, is_read=False).update(is_read=True)
    return redirect('admin_notifications')


@login_required
def mark_notification_read(request, notification_id):
    notif = get_object_or_404(Notification, id=notification_id, user=request.user)
    notif.is_read = True
    notif.save()
    return redirect('admin_notifications')


from django.http import JsonResponse
from .models import Appointment, Doctor

# MONITORING APPOINTMENTS VIEW
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from itertools import groupby
from django.utils.timezone import localtime
from .models import Appointment

@login_required
def monitor_appointments(request):
    """
    Displays appointments grouped by date with AI filter support.
    filter_type = 'with_ai', 'without_ai', or 'all'
    """
    filter_type = request.GET.get('filter', 'all')  # default to 'all'

    if filter_type == 'with_ai':
        # Show only AI Screening appointments
        appointments = Appointment.objects.filter(
            archive=False, is_ai_screening=True
        ).order_by("appointment_datetime")
    elif filter_type == 'without_ai':
        # Show only standard appointments
        appointments = Appointment.objects.filter(
            archive=False, is_ai_screening=False
        ).order_by("appointment_datetime")
    else:
        # Show all appointments (AI + standard)
        appointments = Appointment.objects.filter(
            archive=False
        ).order_by("appointment_datetime")

    # Group appointments by date
    grouped_appointments = {}
    for date, group in groupby(
        appointments, key=lambda a: localtime(a.appointment_datetime).date()
    ):
        grouped_appointments[date] = list(group)

    context = {
        'grouped_appointments': grouped_appointments,
        'filter_type': filter_type
    }
    return render(request, "admin_panel/appointments.html", context)




# views.py
from django.shortcuts import render
from .models import Appointment
from django.db.models import Q
from collections import defaultdict
from django.utils.timezone import localtime

def completed_appointments(request):
    # Fetch all completed appointments, ordered by datetime
    appointments = Appointment.objects.filter(status='Completed').order_by('-appointment_datetime')

    context = {
        'appointments': appointments
    }
    return render(request, 'admin_panel/completed_appointments.html', context)



def update_status(request):
    if request.method == "POST":
        appt_id = request.POST.get("id")
        new_status = request.POST.get("status")
        try:
            appt = Appointment.objects.get(id=appt_id)
            appt.status = new_status
            appt.save()

            response = {
                "success": True,
                "id": appt.id,
                "status": appt.status,
                "booking_for": appt.booking_for,
                "patient_last_name": appt.patient_last_name,
                "patient_first_name": appt.patient_first_name,
                "doctor": appt.doctor.user.get_full_name(),
                "reason": appt.reason,
                "appointment_datetime": localtime(appt.appointment_datetime).strftime("%I:%M %p"),
            }
            return JsonResponse(response)
        except Appointment.DoesNotExist:
            return JsonResponse({"success": False, "error": "Appointment not found."})
    return JsonResponse({"success": False, "error": "Invalid request."})
    


from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from .models import Notification

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def mark_all_read(request):
    notifications = Notification.objects.filter(user=request.user, is_read=False)
    updated = notifications.update(is_read=True)
    return Response(
        {"message": f"{updated} notifications marked as read."},
        status=status.HTTP_200_OK
    )

#CONTROL Z


# views.py
from rest_framework import generics
from .models import Notification
from .serializers import NotificationSerializer

class NotificationDetailAPIView(generics.RetrieveAPIView):
    queryset = Notification.objects.all()
    serializer_class = NotificationSerializer
    lookup_field = 'id'  # ensure URL uses /<id>/


# views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Notification

class NotificationMarkReadView(APIView):
    def post(self, request, pk):
        try:
            notif = Notification.objects.get(pk=pk)
            notif.is_read = True
            notif.save()
            return Response({"success": True})
        except Notification.DoesNotExist:
            return Response({"error": "Not found"}, status=404)


