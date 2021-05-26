import imutils
from imutils.video import VideoStream
import datetime
import json
import time
import cv2
import os
import numpy as np


def surveillance(config):
    # Initialize the camera
    vStream = VideoStream(
        src=config["camera_src"], usePiCamera=config["use_pi_camera"]).start()
    time.sleep(config["camera_start_time"])

    frameAvg = None
    lastUploaded = datetime.datetime.now()
    motionDetected = False
    motionCounter = 0
    uploadsCounter = 0

    while True:
        time.sleep(1.0)
        frame = vStream.read()
        timestamp = datetime.datetime.now()
        message = "No motion"
        motionDetected = False
        frame = imutils.resize(frame, width=500)

        # Proccess frame and compare with previous frames to detect motion
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        gray = cv2.GaussianBlur(gray, (21, 21), 0)
        if frameAvg is None:
            frameAvg = gray.copy().astype("float")
            continue

        cv2.accumulateWeighted(gray, frameAvg, 0.5)
        frameDelta = cv2.absdiff(gray, cv2.convertScaleAbs(frameAvg))
        thresh = cv2.threshold(
            frameDelta, config["delta_threshold"], 255, cv2.THRESH_BINARY)[1]
        thresh = cv2.dilate(thresh, None, iterations=2)
        contours = cv2.findContours(
            thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        contours = imutils.grab_contours(contours)
        for c in contours:
            if cv2.contourArea(c) < config["min_area"]:
                continue
            (x, y, w, h) = cv2.boundingRect(c)
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
            message = "Motion detected"
            motionDetected = True

        ts = timestamp.strftime("%A %d %B %Y %I:%M:%S%p")
        nm = timestamp.strftime("%Y-%m-%d-%I-%M-%S")
        cv2.putText(frame, f"Status: {message}", (10, 20),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 1)
        cv2.putText(frame, ts, (10, frame.shape[0] - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 1)

        # Save the image if motion detected
        if (motionDetected and (timestamp - lastUploaded).seconds >= config["pause_between_uploads"]):
            motionCounter += 1
            if motionCounter >= config["min_motion_frames"]:
                imgPath = f"./images/{nm}.jpg"
                cv2.imwrite(imgPath, frame)
                print(f"Uploaded: {ts}")
                lastUploaded = timestamp
                motionCounter = 0
                uploadsCounter += 1

        else:
            motionCounter = 0

        # Output cam video to the screen
        if config["show_video"]:
            cv2.imshow("Security Feed", frame)
            if config["show_video_treshold"]:
                cv2.imshow("Thresh", thresh)
            if config["show_video_delta"]:
                cv2.imshow("Frame Delta", frameDelta)
            key = cv2.waitKey(1) & 0xFF

        if key == ord("q"):
            break
