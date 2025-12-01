# views.py (or wherever your classify_eye_image view lives)
import os
import io
import logging
import numpy as np
from PIL import Image
from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.models import User
from tensorflow.lite.python.interpreter import Interpreter
import tensorflow as tf

from .models import EyeScreening, Appointment

# Optional OpenCV eye detection
try:
    import cv2
    OPENCV_AVAILABLE = True
except Exception:
    OPENCV_AVAILABLE = False

logger = logging.getLogger(__name__)

# -----------------------------------------------------------
# CONFIGURATION
# -----------------------------------------------------------
LABELS = ["Strabismus", "Strabismus-Free"]
INPUT_SIZE = (224, 224)
CONFIDENCE_THRESHOLD = 0.60

MODEL_PATH = os.path.join(
    settings.BASE_DIR, "admin_panel", "ai_model", "v6_strabismus_mobilenetv2_acc85.tflite"
)

if not os.path.exists(MODEL_PATH):
    raise FileNotFoundError(f"Model not found at: {MODEL_PATH}")

# Load TFLite model
interpreter = Interpreter(model_path=MODEL_PATH)
interpreter.allocate_tensors()
input_details = interpreter.get_input_details()
output_details = interpreter.get_output_details()

# -----------------------------------------------------------
# OPTIONAL: OpenCV Eye Detection
# -----------------------------------------------------------
HAAR_EYE_PATH = None
if OPENCV_AVAILABLE:
    try:
        HAAR_EYE_PATH = cv2.data.haarcascades + "haarcascade_eye.xml"
        if not os.path.exists(HAAR_EYE_PATH):
            HAAR_EYE_PATH = None
    except Exception:
        HAAR_EYE_PATH = None


def detect_eyes_with_opencv(image_bytes, min_eyes=2):
    """Return True if both eyes detected, False if fewer or detection fails."""
    if not OPENCV_AVAILABLE or not HAAR_EYE_PATH:
        return False  # require OpenCV for strict detection
    try:
        pil = Image.open(io.BytesIO(image_bytes)).convert("RGB")
        img = np.array(pil)[:, :, ::-1].copy()  # PIL to OpenCV BGR
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        eyes = cv2.CascadeClassifier(HAAR_EYE_PATH).detectMultiScale(
            gray, scaleFactor=1.1, minNeighbors=5, minSize=(40, 40)
        )
        return len(eyes) >= min_eyes
    except Exception as e:
        logger.exception("Eye detection failed: %s", e)
        return False



def preprocess_image(image_bytes, target_size=INPUT_SIZE):
    """Prepare image for model input."""
    img = Image.open(io.BytesIO(image_bytes)).convert("RGB")
    img = img.resize(target_size, Image.BILINEAR)  # maintain as before, or consider padding to keep aspect ratio
    arr = np.asarray(img).astype(np.float32)
    
    # Old normalization (range [-1, 1])
    # arr = (arr / 127.5) - 1.0

    # ✅ New normalization (range [0,1])
    arr = arr / 255.0

    arr = np.expand_dims(arr, axis=0)
    return arr



# -----------------------------------------------------------
# MAIN ENDPOINT
# -----------------------------------------------------------
@csrf_exempt
def classify_eye_image(request):
    """
    POST /api/classify-eye/
    - Accepts 'image' (file)
    - Optionally 'user_id' / 'username' / 'user_email' (to link record to a user)
    - Optionally Authorization header for Token auth ("Token <token>")
    - Saves result in EyeScreening DB and creates Appointment if user found
    """
    if request.method != "POST":
        return JsonResponse({"status": "error", "message": "Only POST allowed."}, status=405)

    if "image" not in request.FILES:
        return JsonResponse({"status": "error", "message": "No image uploaded."}, status=400)

    try:
        image_file = request.FILES["image"]
        image_bytes = image_file.read()

        # Validate image
        try:
            img = Image.open(io.BytesIO(image_bytes))
            img.verify()
        except Exception:
            return JsonResponse({"status": "error", "message": "Invalid image file."}, status=400)

        # Optional eye detection
        eye_check = detect_eyes_with_opencv(image_bytes)
        if eye_check is False:
            return JsonResponse({
                "status": "error",
                "message": "Please upload a clear photo showing both eyes."
            }, status=400)

        # Preprocess and predict
        input_data = preprocess_image(image_bytes)
        interpreter.set_tensor(input_details[0]["index"], input_data)
        interpreter.invoke()
        raw_output = interpreter.get_tensor(output_details[0]["index"])

        # Interpret model output
        if raw_output.size == 1:
            prob_strabismus_free = float(tf.sigmoid(raw_output).numpy().squeeze())
            prob_strabismus = 1.0 - prob_strabismus_free
            probs = [prob_strabismus, prob_strabismus_free]
        else:
            probs = tf.nn.softmax(raw_output[0]).numpy()

        predicted_idx = int(np.argmax(probs))
        confidence = float(probs[predicted_idx])
        predicted_label = LABELS[predicted_idx]

        if confidence < CONFIDENCE_THRESHOLD:
            return JsonResponse({
                "status": "error",
                "message": "AI is unsure. Please try again with a clearer image.",
                "confidence": round(confidence * 100, 2),
            }, status=400)

        diagnosis = predicted_label
        probs_percent = {LABELS[i]: round(float(probs[i]) * 100, 2) for i in range(len(LABELS))}

        # ---------- Find user ----------
        user = None

        # 1) Try user_id from form
        user_id = request.POST.get("user_id") or request.POST.get("userId") or None
        if user_id:
            try:
                user = User.objects.get(id=int(user_id))
            except Exception:
                user = None

        # 2) Try username
        if not user:
            username = request.POST.get("username") or request.POST.get("user_name")
            if username:
                try:
                    user = User.objects.filter(username=username).first()
                except Exception:
                    user = None

        # 3) Try email
        if not user:
            user_email = request.POST.get("user_email") or request.POST.get("email")
            if user_email:
                try:
                    user = User.objects.filter(email=user_email).first()
                except Exception:
                    user = None

        # 4) Try Authorization header token (DRF TokenAuth common pattern: "Token <key>")
        if not user:
            auth_header = request.META.get("HTTP_AUTHORIZATION", "")
            if auth_header:
                try:
                    parts = auth_header.split()
                    if len(parts) == 2:
                        token_type, token_key = parts
                        # If you use DRF token auth:
                        if token_type.lower() == "token":
                            from rest_framework.authtoken.models import Token
                            tok = Token.objects.filter(key=token_key).first()
                            if tok:
                                user = tok.user
                        # If you use JWT you'd decode here (left as TODO - depends on your JWT lib)
                except Exception:
                    logger.exception("Failed to authenticate from Authorization header")

        # ---------- Save EyeScreening ----------
        screening = EyeScreening.objects.create(
            user=user,
            image=image_file,
            result=diagnosis,
            confidence=confidence * 100,
            remarks=f"AI detected: {diagnosis} ({confidence*100:.2f}% confidence)",
        )

        # ---------- Create Appointment if user found ----------
        if user:
            try:
                Appointment.objects.create(
                    user=user,
                    reason="AI Eye Screening",
                    preliminary_result=f"{diagnosis} ({confidence*100:.2f}% confidence)",
                    archive=False,
                    is_ai_screening=True,
                    # If Appointment model expects other required fields (patient_first_name etc.)
                    # you might need to set defaults or pull from user profile.
                )
            except Exception:
                logger.exception("Failed to create appointment record")

        # ---------- Response ----------
        return JsonResponse({
            "status": "success",
            "diagnosis": diagnosis,
            "confidence": round(confidence * 100, 2),
            "probabilities": probs_percent,
            "screening_id": screening.id,
            "message": (
                "Screening completed. Appointment automatically created for follow-up."
                if (diagnosis == "Strabismus" and user)
                else "You are Strabismus-Free! Appointment created for record purposes." if user else "Screening completed. No linked user found."
            ),
            "proceed_to_booking": True
        }, status=200)

    except Exception as e:
        logger.exception("Error in classify_eye_image: %s", e)
        return JsonResponse({
            "status": "error",
            "message": "Internal server error.",
            "detail": str(e)
        }, status=500)
    


#CONTROL Z
