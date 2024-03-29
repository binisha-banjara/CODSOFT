import cv2
import os
import numpy as np

# Reading the video
vidcap = cv2.VideoCapture('video.mp4')
success, image = vidcap.read()
count = 0
idx = 0

# Read the video frame by frame
while success:
    # Converting into hsv image
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    
    # Green range
    lower_green = np.array([40, 40, 40])
    upper_green = np.array([70, 255, 255])
    
    # Blue range
    lower_blue = np.array([110, 50, 50])
    upper_blue = np.array([130, 255, 255])

    # Red range
    lower_red = np.array([0, 31, 255])
    upper_red = np.array([10, 255, 255])  # Adjusted upper range for Portugal (Lower range remains the same)

    # White range
    lower_white = np.array([0, 0, 0])
    upper_white = np.array([0, 0, 255])

    # Define a mask ranging from lower to upper
    mask = cv2.inRange(hsv, lower_green, upper_green)
    
    # Do masking
    res = cv2.bitwise_and(image, image, mask=mask)

    # Convert to hsv to gray
    res_bgr = cv2.cvtColor(res, cv2.COLOR_HSV2BGR)
    res_gray = cv2.cvtColor(res, cv2.COLOR_BGR2GRAY)

    # Defining a kernel to do morphological operation in threshold image to 
    # get better output.
    kernel = np.ones((13, 13), np.uint8)
    thresh = cv2.threshold(res_gray, 127, 255, cv2.THRESH_BINARY_INV | cv2.THRESH_OTSU)[1]
    thresh = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)

    # Find contours in threshold image
    contours, hierarchy = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    
    font = cv2.FONT_HERSHEY_SIMPLEX

    for c in contours:
        x, y, w, h = cv2.boundingRect(c)

        # Detect players
        if h >= (1.5) * w:
            if w > 15 and h >= 15:
                idx = idx + 1
                player_img = image[y:y+h, x:x+w]
                player_hsv = cv2.cvtColor(player_img, cv2.COLOR_BGR2HSV)

                # If player has blue jersey
                mask1 = cv2.inRange(player_hsv, lower_blue, upper_blue)
                res1 = cv2.bitwise_and(player_img, player_img, mask=mask1)
                res1 = cv2.cvtColor(res1, cv2.COLOR_HSV2BGR)
                res1 = cv2.cvtColor(res1, cv2.COLOR_BGR2GRAY)
                nzCount = cv2.countNonZero(res1)

                # If player has red jersey
                mask2 = cv2.inRange(player_hsv, lower_red, upper_red)
                res2 = cv2.bitwise_and(player_img, player_img, mask=mask2)
                res2 = cv2.cvtColor(res2, cv2.COLOR_HSV2BGR)
                res2 = cv2.cvtColor(res2, cv2.COLOR_BGR2GRAY)
                nzCountred = cv2.countNonZero(res2)

                if nzCount >= 20:
                    # Mark blue jersey players as France
                    cv2.putText(image, 'France', (x-2, y-2), font, 0.8, (255, 0, 0), 2, cv2.LINE_AA)
                    cv2.rectangle(image, (x, y), (x+w, y+h), (255, 0, 0), 3)

                if nzCountred >= 20:
                    # Mark red jersey players as Belgium
                    cv2.putText(image, 'Belgium', (x-2, y-2), font, 0.8, (0, 0, 255), 2, cv2.LINE_AA)
                    cv2.rectangle(image, (x, y), (x+w, y+h), (0, 0, 255), 3)

        if (1 <= h <= 30) and (1 <= w <= 30):
            player_img = image[y:y+h, x:x+w]
            player_hsv = cv2.cvtColor(player_img, cv2.COLOR_BGR2HSV)
            
            # White ball detection
            mask1 = cv2.inRange(player_hsv, lower_white, upper_white)
            res1 = cv2.bitwise_and(player_img, player_img, mask=mask1)
            res1 = cv2.cvtColor(res1, cv2.COLOR_HSV2BGR)
            res1 = cv2.cvtColor(res1, cv2.COLOR_BGR2GRAY)
            nzCount = cv2.countNonZero(res1)

            if nzCount >= 3:
                # Detect football
                cv2.putText(image, 'football', (x-2, y-2), font, 0.8, (0, 255, 0), 2, cv2.LINE_AA)
                cv2.rectangle(image, (x, y), (x+w, y+h), (0, 255, 0), 3)

    cv2.imwrite("./Cropped/frame{}.jpg".format(count), res)
    print('Read a new frame:', success)  # Save frame as JPEG file
    count += 1
    cv2.imshow('Match Detection', image)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
    success, image = vidcap.read()

vidcap.release()
cv2.destroyAllWindows()
