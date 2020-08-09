#import necessary packages
import datetime
import imutils
import json
import numpy as np
import os
import cv2
from write_vid import record_video #for recording the motion
from ftplib import FTP
from clean import cleanup #for optimizing
import threading

# check if config file exist
check= os.path.exists('conf1.json')
if check == True:
    conf = json.load(open("conf1.json")) #loads the values from config file
else:
    conf = json.load(open("default.json")) #default values



cap = cv2.VideoCapture(0)#initialize the capture


ftp = FTP('0.0.0.0')
username= conf["username"]
password= conf["password"]

# print("Longin Done")

abc= ("/add/your/path/here/motion_detection_ftp/save")

ftp.login(username, password) #login to ftp server
def ftp_push(abc, filename): #function for storing file to the server
    ftp.set_pasv(False)
    ftp.storbinary("STOR "+str(filename)+".mp4", open(abc+"/"+str(filename)+".mp4", "rb"), 1024)



def rec_frame():

    avg = None
    motion_counter = 0
    non_motion_timer = conf["nonMotionTimer"]
    fourcc = cv2.VideoWriter_fourcc(*'mp4v') #codec for the recorded video
    writer = None
    (h, w) = (None, None)
    made_recording = False

    if (cap.isOpened() == False):  # check if camera is initialized correctly
        print("Error opening video stream")  # gives error if not initialized

    while cap.isOpened():  # starts a wile loop if initialized correctly
        ret, frame = cap.read()

        timestamp = datetime.datetime.now()
        motion_detected = False


        if not ret:
            print("[INFO] Frame couldn't be grabbed. Breaking - " +
                  datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S"))
            break

        # resize the frame, convert it to grayscale, and blur it
        frame = imutils.resize(frame, width=conf["resizeWidth"])
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        gray = cv2.GaussianBlur(gray, (21, 21), 0) #noise reduction

        # if the average frame is None, initialize it
        if avg is None:
            avg = gray.copy().astype("float")
            continue

        # accumulate the weighted average between the current frame and
        # previous frames, then compute the difference between the current
        # frame and running average
        cv2.accumulateWeighted(gray, avg, 0.5)
        frameDelta = cv2.absdiff(gray, cv2.convertScaleAbs(avg)) #find absolute difference

        #threshold to segmentation
        thresh = cv2.threshold(frameDelta, 5, 255,
                               cv2.THRESH_BINARY)[1]
        thresh = cv2.dilate(thresh, None, iterations=2)
        dilate = cv2.dilate(thresh, None, iterations=3)  # dilate the thresholded frames to fill-in all the holes
        cnts, hir = cv2.findContours(dilate, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

        # loop over the contours
        for c in cnts:
            # if the contour is too small, ignore it
            if cv2.contourArea(c) < conf["min_area"]:
                continue

            # compute the bounding box for the contour, draw it on the frame,
            # and update the text
            (x, y, w1, h1) = cv2.boundingRect(c)
            cv2.rectangle(frame, (x, y), (x + w1, y + h1), (0, 255, 0), 2)
            motion_detected = True #motion check

        fps = int(round(cap.get(cv2.CAP_PROP_FPS)))
        record_fps = 16
        ts = timestamp.strftime("%Y-%m-%d_%H_%M_%S")
        time_and_fps = ts + " - fps: " + str(fps) #displays on the screen

        # draw the text and timestamp on the frame
        cv2.putText(frame, "Motion Detected: {}".format(motion_detected), (10, 20),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)
        cv2.putText(frame, time_and_fps, (10, frame.shape[0] - 10),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.35, (255, 0, 0), 1)

        if writer is None:
            filename = datetime.datetime.now().strftime("%Y-%m-%d_%H_%M_%S") #name of the file
            file_path = (f"/home/AT/PycharmProjects/Demo Projects/motion_detection_ftp/save/{filename}.mp4")
            file_path = file_path.format(filename=filename)

            (h2, w2) = frame.shape[:2]
            writer = cv2.VideoWriter(abc+"/"+str(filename)+".mp4", fourcc, record_fps, (w2, h2), True)

        record_video(frame, writer, h2, w2) #records video

        if motion_detected: #if motion is detected increase the motion counter
            # increment the motion counter
            motion_counter += 1

            # check to see if the number of frames with motion is high enough
            if motion_counter >= conf["min_motion_frames"]: #sensitivity of the motion

                #threading is used to push the recorded file to the ftp server while recording takes place
                t2 = threading.Thread(target=ftp_push, args=(abc, filename))
                t2.start()
                t2.join() #waits till the thread is completed


                record_video(frame, writer, h2, w2)#thread for recording
                cleanup()  # optimization for storage

                made_recording = True
                non_motion_timer = conf["nonMotionTimer"] #checks for motion for x mins

        else:
            if made_recording is True and non_motion_timer > 0:
                non_motion_timer -= 1
            else:
                motion_counter = 0
                if writer is not None:
                    writer.release() #release the writer if motion is not detected
                    writer = None
                if made_recording is False:
                    os.remove(file_path)

                made_recording = False
                non_motion_timer = conf["nonMotionTimer"] #checks for motion for x mins

        # check to see if the frames should be displayed to screen
        cv2.imshow("Feed", frame) #shows the feed
        key = cv2.waitKey(1) & 0xFF

            # if the `q` key is pressed, break from the loop
        if key == ord("q"):

            t2= threading.Thread(target= ftp_push, args= (abc, filename))
            t2.start()
            break

    # cleanup the camera and close any open windows
    cap.release()
    cv2.destroyAllWindows()

#thread keeps the monitoring going
t1= threading.Thread(target= rec_frame)
t1.start()
