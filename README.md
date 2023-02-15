# Classification system for objects on a conveyor
Classification system for objects, which are moving on conveyor.


It's my first big project, which accumulated my current knowledge in  automation/python/computer vision/image classification received from scratch in the past 2021 in free time from university tasks. It's amateur project, and you can find many issues in code and system, but I continue learning and will improve this project and all my new projects after getting new knowledge. Note, I am not a native English speaker and continue to learn it. 

This project uses Raspberry Pi 4B as controller to collect images in dataset and classify objects. Image capture for data collecting or for classification is done by sensor signal (in this case it's E18-D80NK). Movement of conveyor (AC 220V motor) is controls by relay and signal from controller.

<img src="https://github.com/damagedsystem/object-classification-from-conveyor/blob/main/README_content/conveyor.jpg" width="500" height="400">  


The development of the system involves four stages:

1. Creating unlabeled dataset of objects for classification (in training uses Keras method "flow_from_directory" ) by [script 1](https://github.com/damagedsystem/object-classification-from-conveyor/blob/main/1%20get_image_from_conveyor.py).
   Result: 4 class' folders, each contains 100 images of current class (in this case: relay, servo motor, step motor driver,
   and one folder with images of more than 70 unique objects as "false class").
   
Images capturing process:
   
  ![Images capturing process](https://github.com/damagedsystem/object-classification-from-conveyor/blob/main/README_content/image_capturing.gif)   
   
   Classes: 
         
   <img src="https://github.com/damagedsystem/object-classification-from-conveyor/blob/main/README_content/classes.jpg" width="500" height="400">   
   
   Note: In this case, the number of classes is small, but you can use more. Also, objects classifies by only one side view (bottom left). If you need to classify objects in different sides view (like in bottom right), the dataset must contain relevant images. 
   
   <img src="https://github.com/damagedsystem/object-classification-from-conveyor/blob/main/README_content/sides.jpg" width="500" height="300"> 
   
2. Data augmentation part [(script 2)](https://github.com/damagedsystem/object-classification-from-conveyor/blob/main/2%20Data_augmentation_script_.ipynb). 

   Input: 4 folders with 100 images per class.
   
   Ouput: (n+1)-times bigger dataset, which combined original and generated data (in this case 400 images per class).
   Note, need more data for real-using project, but enough for demonstration how this system works.
   
3. Convolutional neural network training [(script 3)](https://github.com/damagedsystem/object-classification-from-conveyor/blob/main/3%20Training_of_CNN_model.ipynb).

   Input: dataset from stage 2.
   
   Output: trained TensorFlow Lite (or .h5) model for custom objects classification.
   (In this case for training was used transfer learning technology (VGG16, imagenet) with fine-tuning. For more, see [script 3](https://github.com/damagedsystem/object-classification-from-conveyor/blob/main/3%20Training_of_CNN_model.ipynb)).
   
4. Running trained TensorFlow Lite model on Raspberry Pi for classification of objects, which are moving on conveyor [(script 4)](https://github.com/damagedsystem/object-classification-from-conveyor/blob/main/4%20Raspberry%20Pi%20TFLite.py).
   Saving current classification session results into PostgreSQL DB.
   
  RESULT (classification process):
  
  ![Classification process](https://github.com/damagedsystem/object-classification-from-conveyor/blob/main/README_content/classification.gif)
  
  Weaknesses:
  
  It's not object detection, so on one image must be one object for correct system work;
  
  Classification time for one object is too big;
  
  The sensor is not suitable for all materials, in particular some materials absorb its radiation.
