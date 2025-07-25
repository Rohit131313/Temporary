# 📚 Student Attendance Portal

A facial recognition and geolocation based attendance system with real-time database storage and a mobile-friendly admin/student dashboard.

---

# 📖 Table of Contents
- [🚀 How to Set Up and Run](#-how-to-set-up-and-run)
  - [1. Clone the Repository](#1-clone-the-repository)
  - [2. Create and Activate a Conda Environment](#2-create-and-activate-a-conda-environment)
  - [3. Install Dlib](#3-install-dlib)
  - [4. Install Project Requirements](#4-install-project-requirements)
  - [5. Configure Firebase, ImageKit, and Environment Variables](#5-configure-firebase-imagekit-and-environment-variables)
    - [5.1 Download serviceAccountKey.json](#51-download-serviceaccountkeyjson)
    - [5.2 Create a .env File](#52-create-a-env-file)
  - [6. Set Up Your Database and Storage](#6-set-up-your-database-and-storage)
  - [7. Run the Server Locally](#7-run-the-server-locally)
  - [8. Access on Mobile (Better Location Accuracy)](#8-access-on-mobile-better-location-accuracy)
- [✅ Done!](#-done-youre-all-set-to-use-the-student-attendance-portal-)

---

## 🚀 How to Set Up and Run

### 1. Clone the Repository
```bash
git clone https://github.com/Rohit131313/Smart-Attendance-System-with-Dual-Authentication-Geolocation-and-Face-Recognition.git
cd Smart-Attendance-System-with-Dual-Authentication-Geolocation-and-Face-Recognition
```

---

### 2. Create and Activate a Conda Environment
```bash
conda create -n attendance-portal python=3.12
conda activate attendance-portal
```

---

### 3. Install Dlib
Download the appropriate `.whl` file for your Python version from [this link](https://github.com/z-mahmud22/Dlib_Windows_Python3.x).

Or install directly (for Python 3.12, Windows 64-bit):
```bash
python -m pip install dlib-19.24.99-cp312-cp312-win_amd64.whl
```

---

### 4. Install Project Requirements
```bash
pip install -r requirements.txt
```

---

### 5. Configure Firebase, ImageKit, and Environment Variables

#### 5.1. Download `serviceAccountKey.json`
- Go to your [Firebase Console](https://console.firebase.google.com/).
- Select your project.
- Navigate to **Project Settings** > **Service Accounts**.
- Click **Generate New Private Key** → It will download the `serviceAccountKey.json` file.
- 📄 *This file contains your Firebase project’s secret keys and credentials needed for server-side authentication.*

#### 5.2. Create a `.env` File
In your project root directory, create a `.env` file and add these environment variables:

```
IMAGEKIT_PUBLIC_KEY=your_imagekit_public_key_here
IMAGEKIT_PRIVATE_KEY=your_imagekit_private_key_here
IMAGEKIT_URL_END_POINT=your_imagekit_url_endpoint_here
DATABASE_URL=your_firebase_database_url_here
FIREBASE_SERVICE_ACCOUNT_KEY_JSON=copy and paste the content of path_to_your_serviceAccountKey.json file
```

**Note:**
- `DATABASE_URL` is your **Firebase Realtime Database URL** (like `https://your-project-id.firebaseio.com/`).

---

### 6. Set Up Your Database and Storage

- Use the `AddDatatoDatabase.py` file provided to populate your **Firebase Realtime Database**.
- The database should follow this format:

```json
{
  "Students": {
    "1": {
      "absent": 1,
      "attendance": {
        "2025-04-16": "absent"
      },
      "batch": "2026",
      "email": "a1@gmail.com",
      "holiday": 0,
      "last_attendace_time": "2025-04-16 09:06:36",
      "major": "IT",
      "name": "a",
      "present": 0,
      "profile_image": "imagekit_url_endpoint/students/1.jpg",
      "total_attendance": 0,
      "uid": "uid should be entered here"
    },
    "2": {
      "absent": 0,
      "attendance": {
        "2025-04-16": "present",
        "2025-04-17": "holiday"
      },
      "batch": "2026",
      "email": "b2@gmail.com",
      "holiday": 1,
      "last_attendace_time": "2025-04-17 09:06:36",
      "major": "IT",
      "name": "b",
      "present": 1,
      "profile_image": "imagekit_url_endpoint/students/2.jpg",
      "total_attendance": 0,
      "uid": "uid should be entered here"
    }
  }
}
```

- Enable **Firebase Authentication** and create users for each student.
- Store each student's **UID** inside the database under their record.
- Upload each student's image to **ImageKit** inside the `students/` folder.
- Update each student's `profile_image` URL according to their uploaded ImageKit image.

---

### 7. Run the Server Locally
```bash
python app.py --host=0.0.0.0 --port=5000
```
Then open [http://localhost:5000](http://localhost:5000) on your **laptop browser**.

---

### 8. Access on Mobile (Better Location Accuracy)

- Open a second terminal.
- Activate the environment again:

```bash
conda activate attendance-portal
```

- Start **ngrok**:

```bash
ngrok http 5000
```

- Copy the generated **ngrok URL** (e.g., `https://randomid.ngrok-free.app`).

- Update `BASE_URL` inside these files:
  - `templates/index.html`
  - `static/adminDashboard.js`

- Now open the **ngrok URL** on your mobile browser.

---

# ✅ Done! You’re all set to use the Student Attendance Portal 🎯

---
