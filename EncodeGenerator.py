import os
import cv2
import face_recognition
import pickle
import numpy as np
import requests
from imagekitio import ImageKit
from dotenv import load_dotenv
from types import SimpleNamespace

load_dotenv()

# ImageKit Credentials
imagekit = ImageKit(
    private_key=os.getenv('IMAGEKIT_PRIVATE_KEY'),
    public_key=os.getenv('IMAGEKIT_PUBLIC_KEY'),
    url_endpoint=os.getenv('IMAGEKIT_URL_END_POINT')
)

# Fetch all images in 'students' folder
def fetch_student_images():
    response = imagekit.list_files()
    # Filter files based on URL containing '/students/'
    student_images = {img.name: img.url for img in response.list if "/students/" in img.url}
    return student_images

# Convert URL to image
def url_to_image(url):
    response = requests.get(url, stream=True)
    if response.status_code == 200:
        image_array = np.asarray(bytearray(response.content), dtype=np.uint8)
        return cv2.imdecode(image_array, cv2.IMREAD_COLOR)
    return None

# Encode faces
def find_encodings(images):
    encode_list = []
    for img in images:
        if img is not None:
            img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            encodings = face_recognition.face_encodings(img)
            if encodings:
                encode_list.append(encodings[0])
    return encode_list

# 🔥 Process Images from ImageKit
print("Fetching images from ImageKit...")
student_images = fetch_student_images()
imgList = []
studentIds = [os.path.splitext(s)[0] for s in student_images.keys()]

for student_id, url in student_images.items():
    img = url_to_image(url)
    if img is not None:
        imgList.append(img)

print("Encoding faces...")
encodeListKnown = find_encodings(imgList)
encodeListKnownWithIds = [encodeListKnown, studentIds]
print(studentIds)
print("Encoding Complete")

# Ensure the previous pickle file is replaced
pickle_file = "EncodeFile.p"
if os.path.exists(pickle_file):
    os.remove(pickle_file)  # Delete existing file before creating a new one

with open(pickle_file, 'wb') as file:
    pickle.dump(encodeListKnownWithIds, file)

print("File Saved Successfully!")
