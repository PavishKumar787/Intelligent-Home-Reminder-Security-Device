from fastapi import APIRouter, UploadFile, File, Form
import face_recognition
from db import load_db, save_db, get_user_by_name
import tempfile
import os

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
        
        # Save to temporary file and use face_recognition's native loader
        temp_path = None
        try:
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
            if temp_path and os.path.exists(temp_path):
                os.unlink(temp_path)

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
