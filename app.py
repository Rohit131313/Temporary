import os
import pickle
import numpy as np
import cv2
import face_recognition
import firebase_admin
from firebase_admin import credentials, db
from datetime import datetime
from flask import Flask, request, jsonify, render_template ,redirect, url_for, session
from dotenv import load_dotenv
import json
from geopy.distance import geodesic
from flask_cors import CORS  
import subprocess
import sys
import threading
import time
from datetime import datetime, timedelta


load_dotenv()

# Initialize Firebase
cred_dict = json.loads(os.getenv('FIREBASE_SERVICE_ACCOUNT_KEY_JSON'))
cred = credentials.Certificate(cred_dict)
firebase_admin.initialize_app(cred, {'databaseURL': os.getenv('DATABASE_URL')})


# Fetch geofence parameters from Firebase
def fetch_geofence_parameters():
    ref = db.reference("AdminLocation")
    admin_location = ref.get()
    
    if admin_location:
        latitude = float(admin_location.get("latitude", 0))
        longitude = float(admin_location.get("longitude", 0))
        radius = int(admin_location.get("radius", 500))  # Default to 500 meters
    else:
        latitude, longitude, radius = 0, 0, 500  # Default values if no data found
    
    return (latitude, longitude), radius

# Update geofence parameters dynamically
GEOFENCE_CENTER, GEOFENCE_RADIUS = fetch_geofence_parameters()
print(GEOFENCE_CENTER)
print(GEOFENCE_RADIUS)

app = Flask(__name__)
CORS(app)

# Auto-mark attendance at 11 PM daily
def auto_mark_attendance():
    while True:
        now = datetime.now()
        target_time = now.replace(hour=23, minute=0, second=0, microsecond=0)
        
        if now >= target_time:
            today = now.strftime("%Y-%m-%d")
            weekday = now.weekday()  # 5 = Saturday, 6 = Sunday
            
            ref = db.reference("Students")
            students = ref.get()
            
            if students:
                for student_id, student_data in students.items():
                    attendance = student_data.get("attendance", {})
                    
                    if today not in attendance:
                        status = "holiday" if weekday in [5, 6] else "absent"
                        db.reference(f"Students/{student_id}/attendance/{today}").set(status)
                        db.reference(f"Students/{student_id}/{status}").set(student_data.get(status, 0) + 1)
                        print(f"Marked {status} for {student_id} on {today}")
            
            time.sleep(86400)  # Wait for 24 hours before checking again

threading.Thread(target=auto_mark_attendance, daemon=True).start()


@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html')

@app.route('/login.html')
def logout():
    return render_template('login.html')

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

@app.route('/adminLogin')
def adminLogin():
    return render_template('adminLogin.html')

@app.route('/adminDashboard')
def adminDashboard():
    return render_template('adminDashboard.html')


@app.route("/process", methods=["POST"])
def process_image():
    if "image" not in request.files:
        return jsonify({"error": "No image received"}), 400
    if "latitude" not in request.form or "longitude" not in request.form:
        return jsonify({"error": "Latitude and longitude required"}), 400

    user_lat = float(request.form["latitude"])
    user_lon = float(request.form["longitude"])
    user_location = (user_lat, user_lon)

    print(GEOFENCE_CENTER)
    print(user_location)
    # Check geofencing
    distance = geodesic(GEOFENCE_CENTER, user_location).meters

    print(f"Distance (geodesic): {distance} meters")
    if distance > GEOFENCE_RADIUS:
        return jsonify({"error": "User is outside the geofenced area."}), 400
    else:
        print("User is in range")

    # Load face encodings
    print("Loading Encode File ...")
    with open('EncodeFile.p', 'rb') as file:
        encodeListKnownWithIds = pickle.load(file)
    encodeListKnown, studentIds = encodeListKnownWithIds
    # print(studentIds)
    
    # Process image
    file = request.files["image"]
    image_bytes = file.read()
    image_np = np.frombuffer(image_bytes, np.uint8)
    img = cv2.imdecode(image_np, cv2.IMREAD_COLOR)
    imgS = cv2.resize(img, (0, 0), None, 0.25, 0.25)
    imgS = cv2.cvtColor(imgS, cv2.COLOR_BGR2RGB)

    # Face detection
    faceCurFrame = face_recognition.face_locations(imgS)
    print(faceCurFrame)
    print(len(faceCurFrame))

    # Ensure 'images' folder exists
    if not os.path.exists("images"):
        os.makedirs("images")

    # Draw rectangle around the detected face and save the image
    for (top, right, bottom, left) in faceCurFrame:
        top, right, bottom, left = top * 4, right * 4, bottom * 4, left * 4  # Scale back the coordinates
        cv2.rectangle(img, (left, top), (right, bottom), (0, 255, 0), 2)  # Green rectangle

    # Save the image with a unique filename
    image_filename = f"images/detected_face_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"
    cv2.imwrite(image_filename, img)
    print(f"Image saved at: {image_filename}")


    # Check if multiple faces are detected
    if len(faceCurFrame) > 1:
        return jsonify({"error": "Multiple faces detected. Ensure only one face is in the frame."}), 400
    encodeCurFrame = face_recognition.face_encodings(imgS, faceCurFrame)

    if not faceCurFrame:
        return jsonify({"error": "No face detected"}), 400

    # Draw rectangle around the detected face
    for (top, right, bottom, left) in faceCurFrame:
        top, right, bottom, left = top * 4, right * 4, bottom * 4, left * 4  # Scale back the coordinates
        cv2.rectangle(img, (left, top), (right, bottom), (0, 255, 0), 2)  # Green rectangle

    THRESHOLD = 0.6

    for encodeFace in encodeCurFrame:
        matches = face_recognition.compare_faces(encodeListKnown, encodeFace)
        faceDis = face_recognition.face_distance(encodeListKnown, encodeFace)
        matchIndex = np.argmin(faceDis)

        print(f"Face Distance: {faceDis[matchIndex]}")  # Debugging
        print(matches[matchIndex])
        if matches[matchIndex] and faceDis[matchIndex] < THRESHOLD:
            student_id = studentIds[matchIndex]
            student_info = db.reference(f'Students/{student_id}').get()

            if student_info:
                last_attendance_time = datetime.strptime(student_info['last_attendance_time'], "%Y-%m-%d %H:%M:%S")
                seconds_elapsed = (datetime.now() - last_attendance_time).total_seconds()

                if seconds_elapsed > 86400:
                    # Mark attendance
                    ref = db.reference(f'Students/{student_id}')
                    
                    
                    # student_info['total_attendance'] += 1
                    # ref.child('total_attendance').set(student_info['total_attendance'])
                    
                    student_info['present'] += 1
                    ref.child('present').set(student_info['present'])

                    today = datetime.now().strftime("%Y-%m-%d")
                    ref.child('attendance').child(today).set("present")
                    
                    ref.child('last_attendance_time').set(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
                    student_info['attendance_marked_already'] = False
                else:
                    student_info['attendance_marked_already'] = True
                print(student_info['total_attendance'])
                return jsonify(student_info)

    return jsonify({"error": "Face not recognized"}), 400


@app.route("/run-encode-generator", methods=["GET"])
def run_encode_generator():
    """Runs EncodeGenerator.py dynamically."""
    try:
        print("🚀 Received request to execute EncodeGenerator.py")
        sys.stdout.flush()  # Ensures logs appear immediately

        result = subprocess.run(
            [sys.executable, "EncodeGenerator.py"], 
            capture_output=True, 
            text=True,
            timeout=30  # Timeout after 30 seconds
        )

        if result.returncode != 0:
            return jsonify({
                "error": "EncodeGenerator script failed.",
                "stderr": result.stderr
            }), 500

        return jsonify({
            "message": "EncodeGenerator script executed successfully.",
            "output": result.stdout
        }), 200

    except Exception as e:
        return jsonify({
            "error": f"Failed to run EncodeGenerator: {str(e)}"
        }), 500

# Admin API to edit attendance
@app.route("/admin/edit-attendance", methods=["POST"])
def edit_attendance():
    data = request.json
    student_id = data.get("student_id")
    date = data.get("date")
    status = data.get("status")  # "present", "absent", "holiday"
    
    if not student_id or not date or not status:
        return jsonify({"error": "Missing student_id, date, or status"}), 400
    
    student_info = db.reference(f'Students/{student_id}').get()
    if student_info:
        prevstatus = student_info["attendance"].get(date, "not marked")
        
        if prevstatus != "not marked":
            # Decrement previous status count
            prev_count = student_info.get(prevstatus, 0)
            db.reference(f"Students/{student_id}/{prevstatus}").set(max(0, prev_count - 1))
    
        # Increment new status count
        new_count = student_info.get(status, 0)
        db.reference(f"Students/{student_id}/{status}").set(new_count + 1)

        db.reference(f"Students/{student_id}/attendance/{date}").set(status)
    else:
        return jsonify({"error":"student_id doesn't exist"}), 400
    return jsonify({"message": "Attendance updated successfully"})

# Admin API to mark a day as a holiday for all students
@app.route("/admin/mark-holiday", methods=["POST"])
def mark_holiday():
    data = request.json
    date = data.get("date")
    
    if not date:
        return jsonify({"error": "Date is required"}), 400
    
    ref = db.reference("Students")
    students = ref.get()
    
    if students:
        for student_id, student_info in students.items():
            prevstatus = student_info.get("attendance", {}).get(date, "not marked")
            
            if prevstatus != "not marked" and prevstatus != "holiday":
                # Decrement previous status count
                prev_count = student_info.get(prevstatus, 0)
                db.reference(f"Students/{student_id}/{prevstatus}").set(max(0, prev_count - 1))

            # Update attendance to "holiday"
            db.reference(f"Students/{student_id}/attendance/{date}").set("holiday")

            # Increment holiday count
            current_holiday_count = student_info.get("holiday", 0)
            db.reference(f"Students/{student_id}/holiday").set(current_holiday_count + (1 if prevstatus != "holiday" else 0))

    return jsonify({"message": "Marked holiday for all students"})


@app.route("/get-attendance", methods=["POST"])
def get_attendance():
    data = request.json
    batch = data["batch"]
    branch = data["branch"]
    date = data["selectedDate"]

    ref = db.reference("Students")
    students = ref.get()

    result = []
    for student_id, s in students.items():
        if s.get("batch") == batch and s.get("major", "").strip() == branch.strip():
            attendance = s.get("attendance", {}).get(date, None)
            remark = s.get("remarks", {}).get(date, None)
            result.append({
                "id": student_id,
                "name": s.get("name"),
                "attendance": attendance,
                "remark": remark
            })
    return jsonify(result)

@app.route("/admin/update-attendance", methods=["POST"])
def update_attendance():
    data = request.json
    sid, date, status, remark = data["student_id"], data["date"], data["status"], data["remark"]

    student_ref = db.reference(f"Students/{sid}")
    student_data = student_ref.get()

    prev_status = student_data.get("attendance", {}).get(date)
    if prev_status:
        student_ref.child(prev_status).set(max(0, student_data.get(prev_status, 0) - 1))

    student_ref.child(status).set(student_data.get(status, 0) + 1)
    student_ref.child("attendance").child(date).set(status)
    student_ref.child("remarks").child(date).set(remark)

    return jsonify({"message": "Updated successfully"})

@app.route('/getAllStudentsData')
def get_all_students_data():
    from firebase_admin import db
    ref = db.reference('Students')
    data = ref.get()
    for student in data.values():
        student.setdefault("attendance", {})  
    return jsonify(data)

@app.route("/getstudentattendance", methods=["POST"])
def get_student_attendance():
    data = request.get_json()
    print("📩 Received data:", data)  # Debug line

    student_id = data.get("student")
    start_date = data.get("start")
    end_date = data.get("end")

    if not student_id or not start_date or not end_date:
        return jsonify({"error": "Missing student ID, start date, or end date"}), 400

    try:
        start = datetime.strptime(start_date, "%Y-%m-%d")
        end = datetime.strptime(end_date, "%Y-%m-%d")
    except ValueError:
        return jsonify({"error": "Invalid date format"}), 400

    delta = (end - start).days + 1

    ref = db.reference(f"Students/{student_id}")
    student_data = ref.get()

    if not student_data:
        return jsonify({"error": "Student not found"}), 404

    attendance = student_data.get("attendance", {})
    result = {}

    for i in range(delta):
        current = start + timedelta(days=i)
        date_str = current.strftime("%Y-%m-%d")
        status = attendance.get(date_str, "not marked").lower()

        if status == "present":
            result[date_str] = 1
        elif status == "absent":
            result[date_str] = 0
        elif status == "holiday":
            result[date_str] = -1
        else:
            result[date_str] = -1

    return jsonify(result)


@app.route('/getStudentData', methods=["POST"])
def get_student_data():
    data = request.json
    if not data or "studentid" not in data:
            return jsonify({"error": "Missing 'studentid' in request body"}), 400
    print("Request Data:", data)
    student_id = data["studentid"]
    ref = db.reference(f"Students/{student_id}")
    student_data = ref.get()
    if not student_data:
            return jsonify({"error": "Student not found"}), 404

    attendance = student_data.get("attendance", {})
    remarks = student_data.get("remarks",{})
    return jsonify({"attendance":attendance,"remarks":remarks}), 200


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)

