# This script is using for automative (by sensor signal) object's image-capturing
# from camera (when objects are moving on conveyor).

import os
import time
import RPi.GPIO as GPIO # Raspberry Pi pins
import cv2              # OpenCV


# Image saving settings:
name_of_class = 'CLASS_NAME' # also a folder name for saving
# Path to directory for saving
save_dir_path = f"/home/pi/YOUR_PATH/{name_of_class}"
# Create saving folder if not exist
if not os.path.exists(save_dir_path):
    os.makedirs(save_dir_path)

# GPIO Mode (BOARD / BCM)
GPIO.setmode(GPIO.BCM) 
# Set GPIO Pins
GPIO_SENSOR = 18 # phisical 12 pin
GPIO_RELAY = 4 # phisical 7 pin
GPIO.setup(GPIO_RELAY, GPIO.OUT)
GPIO.setup(GPIO_SENSOR, GPIO.IN)

#  Signal edge variables
E_signal = 0      # Current value 
E_signal_PREV = 0  # Value at previous iteration 

# Camera setup
cam = cv2.VideoCapture(0)
cam.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cam.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
 
s, img = cam.read() # Get one picture for camera auto-setup

if __name__ == '__main__':
    try:
        while True:
            # Using of falling edge signal to make photo
            # (Sensor output is "0" if there is an object, otherwise "1".
            # So, if step befor sensor output was "1" and this step is "0",
            # then capture image from camera).
            E_signal_PREV = E_signal
            if GPIO.input(GPIO_SENSOR) == 1:
                E_signal = 1
                GPIO.output(GPIO_RELAY, True)
            elif GPIO.input(GPIO_SENSOR) == 0:
                E_signal = 0
            if E_signal_PREV == 1 and E_signal == 0:
                
                # Stop conveyor to make photo
                GPIO.output(GPIO_RELAY, False)
                # There is no need to stop conveyor to make photo.
                # It just helpful for me in dev process  
                
                # Get image
                s, img = cam.read()
                # Crop image to square
                croped = img[:,25:505]
                # Change brightness/constast by changing alpha (0-3) and beta (0-100) 
                res = cv2.convertScaleAbs(croped, alpha = 1.4, beta = 15)
                # Postfix for saving image (number of files in directory)               
                cnt = len(next(os.walk(save_dir_path))[2])  + 1
                # Save image
                cv2.imwrite(f"{save_dir_path}/{save_dir_path.split('/')[-1]}_{cnt}.jpg",res)
                print(f"Class: {name_of_class}. Number of files: {cnt}")
                
                # Turn moving of conveyor on
                GPIO.output(GPIO_RELAY, True)
            
            time.sleep(0.2)
 
    # Stop by pressing CTRL + C    
    except KeyboardInterrupt:
        # Turn moving of conveyor off
        GPIO.output(GPIO_RELAY, False)
        print("Script stopped.")
        GPIO.cleanup()