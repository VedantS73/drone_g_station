import numpy as np
import cv2
import cv2.aruco as aruco


cap = cv2.VideoCapture(0)

while True:
    # Capture frame-by-frame
    ret, frame = cap.read()
    print("frame read")
    # Our operations on the frame come here
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    print("frame operated")
    # Create the ArUco dictionary using getPredefinedDictionary
    aruco_dict = aruco.getPredefinedDictionary(aruco.DICT_4X4_100)
    print("aruco dict created")
    # Create DetectorParameters directly
    parameters = aruco.DetectorParameters()  # Updated line

    corners, ids, rejectedImgPoints = aruco.detectMarkers(gray, aruco_dict, parameters=parameters)
    frame_markers = aruco.drawDetectedMarkers(frame.copy(), corners, ids)

    cv2.imshow('frame_marker', frame_markers)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
