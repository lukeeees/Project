# import libraries
import os
import pandas as pd
from datetime import datetime
import numpy as np
import matplotlib.pyplot as plt
import re
import cv2
import time
import io
from google.cloud import vision
from google.cloud.vision_v1 import types
import mysql.connector
from dotenv import load_dotenv
plt.style.use('fivethirtyeight')

# Get data
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = r'C:\Users\User\Documents\School\ADMN 5015\Project\content\copper-poet-375921-842eaf8d4d40.json'

def video_to_image(path):
    # Load the video file
    video = cv2.VideoCapture(path)

    # Set the initial time
    start_time = time.time()

    # Set the time interval in seconds for capturing snapshots
    interval = 1

    # Set a counter for the saved images
    count = 0

    
    while True:
        # Read a frame from the video
        ret, frame = video.read()
        
        # Check if the frame was successfully read
        if ret:
            # Check if the time interval has passed
            if time.time() - start_time >= interval:
                # Set a new start time
                start_time = time.time()
                
                # Save the frame as a JPG file
                cv2.imwrite(f'snapshot_{count}.jpg', frame)
                
                # Increment the counter
                count += 1
        else:
            # End the loop if there are no more frames
            break
    
    # Release the video file and close all windows
    video.release()
    cv2.destroyAllWindows()
    
def detect_emotions(image_path):
    client = vision.ImageAnnotatorClient()
    
    # Load the image file
    with io.open(image_path, 'rb') as image_file:
        content = image_file.read()
    image = types.Image(content=content)
    
    # Detect the emotions in the image
    response = client.face_detection(image=image)
    faces = response.face_annotations
    
    if not faces:
        return "None"

    # Extract the emotions from the face annotations
    emotions = {}
    for face in faces:
        emotions['joy'] = face.joy_likelihood
        emotions['sorrow'] = face.sorrow_likelihood
        emotions['anger'] = face.anger_likelihood
        emotions['surprise'] = face.surprise_likelihood
    
    max_emotion, max_likelihood = max(emotions.items(), key=lambda x: x[1])
    
    return max_emotion

def save_data_to_database(emotion,path,time):
    # Load environment variables from .env file
    load_dotenv()

    # Connect to the MySQL database
    mydb = mysql.connector.connect(
        host=os.getenv('MYSQL_HOST'),
        user=os.getenv('MYSQL_USER'),
        password=os.getenv('MYSQL_PASSWORD'),
        database=os.getenv('MYSQL_DATABASE')
    )

    # Create a cursor to interact with the database
    cursor = mydb.cursor()

    # Define the query to insert data into the table
    sql = "INSERT INTO emotions (emotions, snap,time) VALUES (%s, %s,%s)"

    # Replace the placeholders with the actual data
    val = (emotion, path,time)
    cursor.execute(sql, val,time)

    # Commit the changes to the database
    mydb.commit()

    # Close the cursor and database connection
    cursor.close()
    mydb.close()



def main():
    path = r"C:\Users\User\Documents\School\ADMN 5015\Project\assets\interview.mp4"
    #video_to_image(path)
    count = 0
    snap = []
    emotion = []
    while count < 24:
        path = f'snapshot_{count}.jpg'
        d = detect_emotions(rf'C:\Users\User\Documents\School\ADMN 5015\{path}')
        creation_time = os.path.getctime(rf'C:\Users\User\Documents\School\ADMN 5015\{path}')
        # Convert the creation time to a datetime object
        creation_datetime = datetime.fromtimestamp(creation_time)

        # Convert the datetime object to a string formatted for MySQL
        mysql_datetime = creation_datetime.strftime('%Y-%m-%d %H:%M:%S')
        save_data_to_database(d,path,mysql_datetime)
        count+=1

if __name__ == "__main__":
    main()    




