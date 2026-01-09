from fastapi import APIRouter, UploadFile, File, Form
import numpy as np
import cv2
import face_recognition
from db import load_db, save_db, get_user_by_name

router = APIRouter()


@router.get("/users")
def get_users():
    """Get list of enrolled user names"""
    users = load_db()
    return [u["name"] for u in users]


@router.post("/re-enroll-face")
async def re_enroll_face(
    name: str = Form(...),
    file: UploadFile = File(...)
):
    try:
        print(f"\n=== Re-Enrollment Request ===", flush=True)
        print(f"Name: {name}", flush=True)
        print(f"File: {file.filename}", flush=True)
        
        # Check if user exists
        user = get_user_by_name(name)
        if not user:
            return {"error": f"User '{name}' not found. Please enroll first."}
        
        # Read uploaded image
        image_bytes = await file.read()
        print(f"Image bytes received: {len(image_bytes)}", flush=True)
        
        # Decode bytes with OpenCV to ensure contiguous uint8 RGB data
        image_array = np.frombuffer(image_bytes, dtype=np.uint8)
        bgr_image = cv2.imdecode(image_array, cv2.IMREAD_UNCHANGED)

        if bgr_image is None:
            print("ERROR decoding image: OpenCV returned None", flush=True)
            return {"error": "Invalid image format"}

        if bgr_image.ndim == 2:
            # Grayscale image – expand to 3 channels
            bgr_image = cv2.cvtColor(bgr_image, cv2.COLOR_GRAY2BGR)
        elif bgr_image.shape[2] == 4:
            # Drop alpha channel if present
            bgr_image = cv2.cvtColor(bgr_image, cv2.COLOR_BGRA2BGR)

        rgb = cv2.cvtColor(bgr_image, cv2.COLOR_BGR2RGB)
        # Force a fresh copy to guarantee strict C-contiguous memory layout for dlib
        rgb = np.array(rgb, dtype=np.uint8, order='C', copy=True)

        print(f"Image decoded via OpenCV: shape={rgb.shape}, dtype={rgb.dtype}, contiguous={rgb.flags['C_CONTIGUOUS']}", flush=True)

        # Use face_recognition to detect faces and get encodings
        try:
            face_locations = face_recognition.face_locations(rgb)
            print(f"Face locations found: {len(face_locations)}", flush=True)
            
            if not face_locations:
                print("ERROR: No face detected in image", flush=True)
                return {"error": "No face detected. Please upload a clear photo with a visible face."}
            
            encodings = face_recognition.face_encodings(rgb, face_locations)
            print(f"Encodings extracted: {len(encodings)}", flush=True)
            
        except Exception as e:
            print(f"ERROR in face detection/encoding: {e}", flush=True)
            return {"error": f"Face processing failed: {str(e)}"}
            
        if not encodings:
            return {"error": "Could not extract face encoding. Please try a different photo."}

        # Update user's face encoding in database
        new_encoding = encodings[0].tolist()
        users = load_db()
        
        for u in users:
            if u["name"] == name.lower():
                # Replace all existing encodings with the new one
                u["face_encodings"] = [new_encoding]
                # Also clear old single encoding if present
                if "face_encoding" in u:
                    del u["face_encoding"]
                save_db(users)
                print(f"✓ Face re-enrolled successfully for: {name}", flush=True)
                return {"status": f"Face updated successfully for {name}"}

        return {"error": "User not found"}
        
    except Exception as e:
        print(f"ERROR in re-enrollment: {e}", flush=True)
        import traceback
        traceback.print_exc()
        return {"error": f"Re-enrollment failed: {str(e)}"}
