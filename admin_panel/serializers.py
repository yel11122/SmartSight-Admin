from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Doctor, Appointment, DoctorAvailability, Notification, EyeScreening
import datetime
from django.utils import timezone
import datetime

from rest_framework import serializers
from django.contrib.auth.models import User
from .models import UserProfile

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    date_of_birth = serializers.DateField(required=False, allow_null=True)
    gender = serializers.CharField(required=False, allow_blank=True)

    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email', 'password', 'date_of_birth', 'gender')

    def create(self, validated_data):
        date_of_birth = validated_data.pop('date_of_birth', None)
        gender = validated_data.pop('gender', None)

        # Create the user
        user = User.objects.create_user(
            username=validated_data['email'],
            email=validated_data['email'],
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', ''),
            password=validated_data['password'],
        )

        # Create the UserProfile
        profile, _ = UserProfile.objects.get_or_create(user=user)
        if date_of_birth:
            profile.date_of_birth = date_of_birth
        if gender:
            profile.gender = gender.lower()
        profile.save()

        return user


class DoctorSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()

    class Meta:
        model = Doctor
        fields = ['id', 'full_name', 'specialty', 'is_pediatric']

    def get_full_name(self, obj):
        if obj.user:
            return obj.user.get_full_name() or obj.user.username
        return "Doctor"


class DoctorAvailabilitySerializer(serializers.ModelSerializer):
    doctor_name = serializers.SerializerMethodField()

    class Meta:
        model = DoctorAvailability
        fields = ['id', 'doctor', 'doctor_name', 'date', 'time_slots']

    def get_doctor_name(self, obj):
        if obj.doctor and obj.doctor.user:
            return obj.doctor.user.get_full_name() or obj.doctor.user.username
        return "Doctor"

from rest_framework import serializers
from django.utils import timezone
from .models import Appointment

class AppointmentSerializer(serializers.ModelSerializer):
    doctor_name = serializers.SerializerMethodField()
    appointment_datetime_str = serializers.SerializerMethodField()
    date = serializers.SerializerMethodField()
    time = serializers.SerializerMethodField()
    firstName = serializers.CharField(source='patient_first_name')
    lastName = serializers.CharField(source='patient_last_name')
    age = serializers.IntegerField(source='patient_age')
    gender = serializers.CharField(source='patient_gender')
    bookingFor = serializers.CharField(source='booking_for')

    # Conditional fields
    reason = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    preliminary_result = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    is_ai_screening = serializers.BooleanField(default=True)

    class Meta:
        model = Appointment
        fields = [
            'id',
            'doctor_name',
            'appointment_datetime_str',
            'date',
            'time',
            'firstName',
            'lastName',
            'patient_email',
            'age',
            'gender',
            'reason',
            'bookingFor',
            'status',
            'preliminary_result',
            'is_ai_screening',
        ]

    def get_doctor_name(self, obj):
        if obj.doctor and obj.doctor.user:
            return obj.doctor.user.get_full_name()
        return "Doctor"

    def get_appointment_datetime_str(self, obj):
        return obj.appointment_datetime.isoformat() if obj.appointment_datetime else None

    def get_date(self, obj):
        if obj.appointment_datetime:
            local_dt = timezone.localtime(obj.appointment_datetime)
            return local_dt.strftime("%B %d, %Y")
        return None

    def get_time(self, obj):
        if obj.appointment_datetime:
            local_dt = timezone.localtime(obj.appointment_datetime)
            return local_dt.strftime("%I:%M %p")
        return None

    def validate(self, data):
        # Detect AI Screening
        is_ai = data.get('is_ai_screening', True)

        # For AI Screening, require preliminary_result and remove reason
        if is_ai:
            data['reason'] = None
            if not data.get('preliminary_result'):
                raise serializers.ValidationError({"preliminary_result": "Preliminary result is required for AI Screening."})
        else:
            data['preliminary_result'] = None
            if not data.get('reason'):
                raise serializers.ValidationError({"reason": "Reason is required for standard appointments."})

        # Parse appointment_datetime_str
        full_datetime_str = self.initial_data.get('appointment_datetime_str') or data.get('appointment_datetime_str')
        if not full_datetime_str:
            raise serializers.ValidationError({"appointment_datetime_str": "This field is required."})

        formats_to_try = [
            "%Y-%m-%d %I:%M %p",
            "%Y-%m-%d %H:%M",
            "%Y-%m-%dT%H:%M:%S.%fZ",
            "%Y-%m-%dT%H:%M:%S.%f",
            "%Y-%m-%dT%H:%M:%S",
            "%Y-%m-%dT%H:%M",
        ]

        parsed_dt = None
        import datetime
        for fmt in formats_to_try:
            try:
                parsed_dt = datetime.datetime.strptime(full_datetime_str, fmt)
                parsed_dt = timezone.make_aware(parsed_dt, timezone.get_default_timezone())
                break
            except (ValueError, TypeError):
                continue

        if not parsed_dt:
            raise serializers.ValidationError({"appointment_datetime_str": "Invalid datetime format. Expected e.g. '2025-09-16 09:00 AM'."})

        data['appointment_datetime'] = parsed_dt
        data.pop('appointment_datetime_str', None)
        return data



# --- NOTIFICATION SERIALIZER (NEW) ---
class NotificationSerializer(serializers.ModelSerializer):
    """
    Serializer for the Notification model, exposing key fields
    needed by the mobile application.
    """
    class Meta:
        model = Notification
        # We only need to expose the fields required for display and update (is_read)
        fields = [
            'id', 
            'title', 
            'message', 
            'url', 
            'is_read', 
            'created_at'
        ]
        # Only 'is_read' can be updated by a PUT/PATCH request from the client
        read_only_fields = ['id', 'title', 'message', 'url', 'created_at']



from .models import EyeScreening

class EyeScreeningSerializer(serializers.ModelSerializer):
    user_name = serializers.SerializerMethodField()

    class Meta:
        model = EyeScreening
        fields = ['id', 'user', 'user_name', 'image', 'result', 'confidence', 'created_at', 'appointment']

    def get_user_name(self, obj):
        return obj.user.get_full_name() if obj.user else None
    


#CONTROL Z