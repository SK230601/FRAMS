import cv2;
import numpy as np;
import face_recognition;
import os;
from datetime import datetime;
import attendance

def preprocessing_of_file_system_images():
    # initializing data variables
    imagesPath = 'Raw_Dataset_Train'
    images = []
    personNames = []

    # reading images path from directory for face encodings
    namesList = os.listdir(imagesPath)
    # print(namesList)

    for img in namesList:
        currentImg = cv2.imread(f'{imagesPath}/{img}')
        # storing cv2 obejcts in images
        images.append(currentImg)
        # storing names of images in person names
        personNames.append(img.split('.')[0])
    # print(personNames)
        
    return images, personNames

def findEncodings(images):
    encodingList = []
    for img in images:
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        encodings = face_recognition.face_encodings(img, num_jitters=1, model="small")[0]
        encodingList.append(encodings)
    return encodingList

def predict_result_cam():
    # print("Entering predict_result_cam function")
    capture = cv2.VideoCapture(0)
    images, personNames = preprocessing_of_file_system_images()
    encodingListOKI = findEncodings(images)
    # print(f'{len(encodingListOKI)} Encoding Done.')

    while True:
        # Grabbing a single frame of Video
        success, img = capture.read()

        imgS = cv2.resize(img,(0,0), None, 0.25, 0.25)
        imgS = cv2.cvtColor(imgS, cv2.COLOR_BGR2RGB)

        facesCurrentFrame = face_recognition.face_locations(imgS)
        encodesCurrentFrame = face_recognition.face_encodings(imgS,facesCurrentFrame, num_jitters=1, model="small")

        for encodeFace, faceLocation in zip(encodesCurrentFrame, facesCurrentFrame):
            matches = face_recognition.compare_faces(encodingListOKI, encodeFace, tolerance=0.5)
            faceDistance = face_recognition.face_distance(encodingListOKI, encodeFace)
            # print(faceDistance)
            matchesIndex = np.argmin(faceDistance)

            if matches[matchesIndex]:
                user_id = personNames[matchesIndex].split("_")[0]
                name = personNames[matchesIndex].split("_")[1] + " " + personNames[matchesIndex].split("_")[2]
                fname = personNames[matchesIndex].split("_")[1]
                # print(name)
                c1, c2, c3, c4 = faceLocation
                y1, x2, y2, x1 = c1 * 4, c2 * 4, c3 * 4, c4 * 4

                # Bounding box
                border_thickness = 2
                cv2.rectangle(img, (x1 - border_thickness, y1 - border_thickness),
                              (x2 + border_thickness, y2 + border_thickness), (0, 255, 0), 1)
                
                # Draw a border around the bounding box with square ends
                thicker_ends_size = 4
                border_thickness = 3

                # Top left corner
                cv2.rectangle(img, (x1 - thicker_ends_size, y1 - border_thickness), (x1 + border_thickness, y1 + thicker_ends_size),
                            (0, 255, 0), -1)

                # Top right corner
                cv2.rectangle(img, (x2 - border_thickness, y1 - thicker_ends_size), (x2 + thicker_ends_size, y1 + border_thickness),
                            (0, 255, 0), -1)

                # Bottom left corner
                cv2.rectangle(img, (x1 - thicker_ends_size, y2 - border_thickness), (x1 + border_thickness, y2 + thicker_ends_size),
                            (0, 255, 0), -1)

                # Bottom right corner
                cv2.rectangle(img, (x2 - border_thickness, y2 - thicker_ends_size), (x2 + thicker_ends_size, y2 + border_thickness),
                            (0, 255, 0), -1)

                # Top Name Text
                cv2.putText(img, user_id + " " + fname, (x1 + 6, y1 - 12), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)

                # attendance code
                target_Time_for_in = datetime.strptime('12:10:00','%H:%M:%S').time()
                target_Time_for_out = datetime.strptime('17:30:00','%H:%M:%S').time()
                nowtime = datetime.now().time()

                if nowtime < target_Time_for_in:
                    attendance.markCheckInAttendances(user_id, name)
                elif nowtime > target_Time_for_out:
                    attendance.markCheckOutAttendances(user_id, name)
                elif nowtime > target_Time_for_in and nowtime < target_Time_for_out:
                    attendance.markBreakOut(user_id, name)
                # markCheckInAttendances(name)

        # Display the resulting image
        cv2.imshow("webcam", img)

        # Hit 'p' on the keyboard to quit!
        if cv2.waitKey(1) & 0xFF == ord('p'):
            break

    # Release handle to the webcam
    capture.release()
    cv2.destroyAllWindows()

predict_result_cam()


