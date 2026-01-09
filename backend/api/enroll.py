from fastapi import APIRouter, UploadFile, File, Form
import numpy as np
import face_recognition
from db import add_user
import cv2

router = APIRouter()


@router.post("/enroll-face")
async def enroll_face(
    name: str = Form(...),
    file: UploadFile = File(...)
):
    try:
        print(f"\n=== Enrollment Request ===", flush=True)
        print(f"Name: {name}", flush=True)
        print(f"File: {file.filename}", flush=True)
        
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
            # Detect face locations first
            face_locations = face_recognition.face_locations(rgb)
            print(f"Face locations found: {len(face_locations)}", flush=True)
            
            if not face_locations:
                print("ERROR: No face detected in image", flush=True)
                return {"error": "No face detected. Please upload a clear photo with a visible face."}
            
            # Get face encodings for detected faces
            encodings = face_recognition.face_encodings(rgb, face_locations)
            print(f"Encodings extracted: {len(encodings)}", flush=True)
            
        except Exception as e:
            print(f"ERROR in face detection/encoding: {e}", flush=True)
            import traceback
            traceback.print_exc()
            return {"error": f"Face processing failed: {str(e)}"}
            
        if not encodings:
            print("ERROR: Could not extract face encoding", flush=True)
            return {"error": "Could not extract face encoding. Please try a different photo."}

        # Save user with face_encoding (single 128-dim vector)
        user = {
            "name": name.lower(),
            "face_encoding": encodings[0].tolist()
        }

        try:
            add_user(user)
            print(f"✓ Successfully enrolled: {name}", flush=True)
            return {
                "status": "success",
                "message": f"{name} enrolled successfully"
            }
        except Exception as e:
            print(f"ERROR saving to database: {e}", flush=True)
            import traceback
            traceback.print_exc()
            return {"error": f"Failed to save user: {str(e)}"}
    
    except Exception as e:
        print(f"ERROR in enroll endpoint: {e}", flush=True)
        import traceback
        traceback.print_exc()
        return {"error": f"Enrollment failed: {str(e)}"}
