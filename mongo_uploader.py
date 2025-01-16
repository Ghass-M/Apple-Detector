from pymongo import MongoClient
import gridfs
import os

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler



# Connect to MongoDB
uri = "mongodb+srv://AppleDetector:AppleDetector@cluster0.fjklw.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
# Create a client
client = MongoClient(uri)
# Access the database
db = client["AppleDetector"]
fs = gridfs.GridFS(db)



# Define the directory to monitor
watch_directory = 'static/images'

# Define event handler to monitor the directory
class ImageEventHandler(FileSystemEventHandler):
    def on_created(self, event):
        if event.is_directory:
            return
        # Check if the file is an image
        if event.src_path.endswith(('.png', '.jpg', '.jpeg')):  
            print(f"New image detected: {event.src_path}")
            
            # Open the image file in binary mode and store it in MongoDB
            with open(event.src_path, "rb") as image_file:
                file_id = fs.put(image_file, filename=os.path.basename(event.src_path))
                print(f"Image saved to MongoDB with file ID: {file_id}")


# Set up directory observer
event_handler = ImageEventHandler()
observer = Observer()
observer.schedule(event_handler, watch_directory, recursive=False)

# Start monitoring the directory
observer.start()

# Keep the app running indefinitely
try:
    # This keeps the program alive and observing the directory
    while True:
        pass
except KeyboardInterrupt:
    # Stop the observer gracefully when interrupted
    print("Stopping observer...")
    observer.stop()

# Wait for the observer thread to finish
observer.join()