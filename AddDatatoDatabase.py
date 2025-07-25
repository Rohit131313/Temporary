import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
from dotenv import load_dotenv
import os

load_dotenv() 

cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred, {
    'databaseURL': os.getenv('DATABASE_URL')
})

ref = db.reference('Students/')

data = {
    
}

for key, value in data.items():
    ref.child(key).set(value)