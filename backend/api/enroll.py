from fastapi import APIRouter, UploadFile, File, Form, Request
import numpy as np
import face_recognition
from db import add_user
import tempfile
import os

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
        
        # Save to temporary file and use face_recognition's native loader
        # This is the most reliable way to load images for face_recognition
        temp_path = None
        try:
            # Create temp file with proper extension
            suffix = os.path.splitext(file.filename)[1] if file.filename else '.jpg'
            with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as temp_file:
                temp_file.write(image_bytes)
                temp_path = temp_file.name
            
            print(f"Temp file created: {temp_path}", flush=True)
            
            # Use face_recognition's native image loader
            rgb = face_recognition.load_image_file(temp_path)
            print(f"Image loaded via face_recognition: shape={rgb.shape}, dtype={rgb.dtype}", flush=True)
            
        except Exception as e:
            print(f"ERROR loading image: {e}", flush=True)
            return {"error": "Invalid image format"}
        finally:
            # Clean up temp file
            if temp_path and os.path.exists(temp_path):
                os.unlink(temp_path)

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
