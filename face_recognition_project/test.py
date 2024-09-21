from sklearn.neighbors import KNeighborsClassifier
import cv2
import pickle
import numpy as np
import os
import csv
import time
from datetime import datetime
from win32com.client import Dispatch

date = ''

def speak(str1):
    speak = Dispatch("SAPI.SpVoice")
    speak.Speak(str1)

video = cv2.VideoCapture(0)
facedetect = cv2.CascadeClassifier('data/haarcascade_frontalface_default.xml')

# Load faces and labels
with open('data/names.pkl', 'rb') as w:
    LABELS = pickle.load(w)
with open('data/faces.pkl', 'rb') as f:
    FACES = pickle.load(f)

# Debugging: Print the shapes of FACES and LABELS
print(f"Shape of FACES: {FACES.shape}")
print(f"Length of LABELS: {len(LABELS)}")

# Ensure FACES and LABELS have the same length
if len(FACES) != len(LABELS):
    print(f"Inconsistent data: {len(FACES)} faces and {len(LABELS)} labels.")
    min_length = min(len(FACES), len(LABELS))
    FACES = FACES[:min_length]
    LABELS = LABELS[:min_length]
    print(f"Trimmed data to {min_length} samples.")

knn = KNeighborsClassifier(n_neighbors=30)
knn.fit(FACES, LABELS)

imgBackground = cv2.imread("background.png")

COL_NAMES = ['NAME', 'TIME']

while True:
    ret, frame = video.read()
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = facedetect.detectMultiScale(gray, 1.3, 5)
    for (x, y, w, h) in faces:
        crop_img = frame[y:y+h, x:x+w, :]
        resized_img = cv2.resize(crop_img, (50, 50)).flatten().reshape(1, -1)
        output = knn.predict(resized_img)
        ts = time.time()
        date = datetime.fromtimestamp(ts).strftime("%d-%m-%Y")
        timestamp = datetime.fromtimestamp(ts).strftime("%H:%M-%S")
        
        # Check if the file exists
        exist = os.path.isfile("Attendance/Attendance_" + date + ".csv")
        
        cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 0, 255), 1)
        cv2.rectangle(frame, (x, y), (x+w, y+h), (50, 50, 255), 2)
        cv2.rectangle(frame, (x, y-40), (x+w, y), (50, 50, 255), -1)
        cv2.putText(frame, str(output[0]), (x, y-15), cv2.FONT_HERSHEY_COMPLEX, 1, (255, 255, 255), 1)
        cv2.rectangle(frame, (x, y), (x+w, y+h), (50, 50, 255), 1)
        
        attendance = [str(output[0]), str(timestamp)]
        
    imgBackground[162:162 + 480, 55:55 + 640] = frame
    cv2.imshow("Frame", imgBackground)
    
    k = cv2.waitKey(1)
    if k == ord('o'):
        speak("Attendance Taken..")
        time.sleep(3)
        
        # Append or create the attendance file
        with open("Attendance/Attendance_" + str(date) + ".csv", "a") as csvfile:
            writer = csv.writer(csvfile)
            if exist:
                writer.writerow(attendance)
            else:
                writer.writerow(COL_NAMES)
                writer.writerow(attendance)
    
    if k == ord('q'):
        break

video.release()
cv2.destroyAllWindows()
