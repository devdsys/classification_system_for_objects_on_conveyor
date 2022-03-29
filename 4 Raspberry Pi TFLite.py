# This script is using for automative (by signal from sensor) objects' classification, 
# which are moving on conveyor

import sys
import time
import RPi.GPIO as GPIO # Raspberry Pi pins
import psycopg2         # For access to PostgreSQL DB 
import numpy as np 
import cv2              # OpenCV library
from tflite_runtime.interpreter import Interpreter # For TFLite model
# To install tflite_runtime.interpreter  use:
# pip3 install --extra-index-url https://google-coral.github.io/py-repo tflite_runtime


# Connect to PostgreSQL
try:
    conn_pg = psycopg2.connect('host=192.168.0.100 user=postgres password=psswd_to_db dbname=name_of_db')
except:
    print('Not connected.')
    sys.exit(0)
cur = conn_pg .cursor()


# Raspberry Pi pins setup block

# GPIO Mode (BOARD / BCM)
GPIO.setmode(GPIO.BCM) 
# Set GPIO Pins
GPIO_SENSOR = 18 # phisical 12 pin
GPIO_RELAY = 4   # phisical 7 pin
GPIO.setup(GPIO_RELAY, GPIO.OUT)
GPIO.setup(GPIO_SENSOR, GPIO.IN)

#  Signal edge variables
E_signal = 0       # Current value 
E_signal_PREV = 0  # Value at previous iteration 


# Camera setup block 

cam = cv2.VideoCapture(0)
cam.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cam.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
 
s, img = cam.read() # Get one picture for camera auto-setup


# TFLite model and classes setup block

classes = ["false_object","relay","servo","st_motor_driver"] # Class names (this order is important!)
cnt_classes = [0,0,0,0]                                      # Accumulator for recognized classes of current session
model_path = 'model_adam_v01.tflite'                         # Trained and converted to TFLite model
interpreter = Interpreter(model_path)
print("Model Loaded Successfully.")

interpreter.allocate_tensors()
input_details = interpreter.get_input_details()
output_details = interpreter.get_output_details()


def stop_system():
     # Stop conveyor
    GPIO.output(GPIO_RELAY, False)
    GPIO.cleanup()
    # Add current session relults record to DB
    cur.execute(f"insert into classification_session \
            (false_object, relay, servo, st_motor_driver)\
            values({cnt_classes[0]}, {cnt_classes[1]}, {cnt_classes[2]}, \
            {cnt_classes[3]});")
    conn_pg .commit()
    # Close all connections and stop programm
    cur.close()
    conn_pg .close()


# Classification loop
if __name__ == '__main__':
    try:
        while True:
            try:     
                # Using of falling edge signal to make photo and prediction
                # (Sensor output is "0" if there is an object, otherwise "1".
                # So, if previous step sensor output was "1" and this step is "0", 
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
                    # Get image
                    s, img = cam.read()
                    # Crop image to square
                    cropped = img[:,25:505]
                    # Change brightness/constast by changing alpha (0-3) and beta (0-100) 
                    corrected = cv2.convertScaleAbs(cropped, alpha = 1.4, beta = 15)
                    
                    img = cv2.resize(corrected, (256,256), interpolation = cv2.INTER_AREA)
                
                    #
                    ###
                    input_shape = input_details[0]['shape']
                    input_tensor= np.array(np.expand_dims(img,0), dtype=np.float32)
                    
                    input_index = interpreter.get_input_details()[0]["index"]
                    interpreter.set_tensor(input_index, input_tensor)
                    interpreter.invoke()
                    output_details = interpreter.get_output_details()
                    
                    output_data = interpreter.get_tensor(output_details[0]['index'])
                    pred = np.squeeze(output_data)
                    res = np.argmax(pred)
                    print(f"Class: {classes[res]}")
                    # REFERENCE: https://towardsdev.com/custom-image-classification-model-using-tensorflow-lite-model-maker-68ee4514cd45  
                    ###
                    #

                    # Signall processing block
                    # In current system version does not use any mechanism for reaction on predicted class,
                    # but you can add something here if you use.
                    if res == 0:    # Class "false_object" 
                        cnt_classes[0]+=1
                    elif res ==1:   # Class "relay"
                        cnt_classes[1]+=1
                    elif res ==2:   # Class "servo"
                        cnt_classes[2]+=1
                    elif res ==3:   # Class "st_motor_driver"
                        cnt_classes[3]+=1
                        
                    # Turn moving of conveyor on
                    GPIO.output(GPIO_RELAY, True)
                
                time.sleep(0.2)
            except Exception as e:
                # If something went wrong:
                # call stop_system funtion and end work
                stop_system()
                print("Something went wrong. System stopped.")
                print(f"Error: {e}")
                sys.exit(0)

    # Stop system by pressing CTRL + C    
    except KeyboardInterrupt:
        # Stop conveyor and other elements of system
        stop_system()
        # Print session results to console
        print("By current session was classified:")
        print(f"false_object: {cnt_classes[0]}, relay: {cnt_classes[1]}, servo: {cnt_classes[2]}, st_motor_driver: {cnt_classes[3]}.")
        print("System stopped.")
        sys.exit(0)
