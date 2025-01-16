import os
import firebase_admin
from firebase_admin import credentials, storage, db
from flask import Flask, request, jsonify, render_template
from flask_socketio import SocketIO, emit
import uuid
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import time

# Initialize Flask app and SocketIO
app = Flask(__name__)
socketio = SocketIO(app)

# Initialize Firebase Admin SDK
cred = credentials.Certificate('creds.json')
firebase_admin.initialize_app(cred, {
    'storageBucket': "appledetector-24532.firebasestorage.app",  # Change to your Firebase Storage Bucket
    'databaseURL': 'https://appledetector-24532-default-rtdb.europe-west1.firebasedatabase.app'  # Change to your Realtime DB URL
})
# Define the directory to monitor
watch_directory = '/home/ghassen/Desktop/AppleDetector/static/images'

# Initialize Firebase Storage
bucket = storage.bucket()

# Function to upload the image to Firebase Storage
def upload_image_to_firebase(image_path):
    try:
        blob = bucket.blob(os.path.basename(image_path))
        blob.upload_from_filename(image_path)
        # Make the image publicly accessible
        blob.make_public()
        print(f"Uploaded {image_path} to Firebase Storage")
        # Get the public URL of the uploaded image
        image_url = blob.public_url
        # Store the image URL in Firebase Realtime Database
        save_image_url_to_firebase(image_url,"fresh")
    except Exception as e:
        print(f"Error uploading image: {e}")

# Function to save the image URL in Firebase Realtime Database
def save_image_url_to_firebase(image_url, message):
    try:
        ref = db.reference('images')
        ref.push({'url': image_url, 'message': message})
        print(f"Saved image URL to Firebase Realtime Database: {image_url}")
    except Exception as e:
        print(f"Error saving image URL: {e}")

# Define event handler to monitor the directory
class ImageEventHandler(FileSystemEventHandler):
    def on_created(self, event):
        if event.is_directory:
            return
        if event.src_path.endswith(('.png', '.jpg', '.jpeg')):  # Only process image files
            print(f"New image detected: {event.src_path}")
            upload_image_to_firebase(event.src_path)

# Set up directory observer
event_handler = ImageEventHandler()
observer = Observer()
observer.schedule(event_handler, watch_directory, recursive=False)

# Start monitoring the directory
observer.start()

# Route to serve index.html
@app.route('/')
def index():
    # Get the list of image URLs from Firebase Realtime Database
    ref = db.reference('images')
    images = ref.get()
    return render_template('index.html', images=images)

# Run the Flask app with SocketIO
if __name__ == '__main__':
    print("Monitoring directory for new images...")
    try:
        # Start Flask and SocketIO
        socketio.run(app, host='0.0.0.0', port=5000)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()