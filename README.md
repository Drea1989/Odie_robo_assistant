# Odie the RoboAssistant
In this project i will build my first robo assistant, Odie

## Introduction

This build includes Open Source products created by 3rd parties, the leverage of existing solutions makes the product more robust and speeds up the implementation, there is no need to reinvent the wheel.

### Author
Andrea Balzano, AI Engineer with background in computer science and physics.

### Project goals
create a robo-assistant using Raspberry PI, it's features will be built-up step by step increasing scope and complexity as it goes.

this documentation includes both hardware and software implementation.

the hardware is mostly made of plug and play kits since the scope of the build is the AI that controls the robot's functions.

### hardware components
------
* Raspberry PI 3
* Alphabot 2 for PI
* Raspberry PI camera
* HC-SR04 sonar sensors
* battery Pack
* Backend Server

### OS supported
------
this build is designed for the following OS:

Raspberry PI

* Rasbian 8.0 Jessie

Backend Server

* Ubuntu 16.04

## Software required

### Raspberry PI

Install Rasbian NOOBS available [here](https://www.raspberrypi.org/downloads/noobs/) and then proceed with the installation of the software required for the robot to complete it's tasks.

##### Connect to the PI

follow the guides to connect over [VNC](https://www.raspberrypi.org/documentation/remote-access/vnc/) or [SSH - X11](https://www.raspberrypi.org/documentation/remote-access/) for you desktop or laptop to control the PI remotely.

##### Install Software

first upgrade all components 
```
$ sudo apt-get update
$ sudo apt-get upgrade
$ sudo rpi-update
```
and reboot after firmware update
```
$ sudo reboot
```
install a few developer tools:
```
$ sudo apt-get install build-essential git cmake pkg-config
```
Now we need image and video I/O packages to allow us to load various file formats as well as work with video streams:

```
$ sudo apt-get install libjpeg-dev libtiff5-dev libjasper-dev libpng12-dev
$ sudo apt-get install libavcodec-dev libavformat-dev libswscale-dev libv4l-dev
$ sudo apt-get install libxvidcore-dev libx264-dev
```
We need to install the GTK development library so we can compile the `highgui` sub-module of OpenCV, which allows us to display images to our screen and build simple GUI interfaces:
```
$ sudo apt-get install libgtk2.0-dev
```

#### OpenCV
------
follow the installation guide
[OpenCV Documentation](http://opencv.org/)

#### Snowboy
------
follow the installation guide
[Snowboy Documentation](https://snowboy.kitt.ai/)

#### Pico TTS

fist install editor to change source file

```
$ sudo apt-get install gedit
```

then uncomment the *deb-src* line using:

```
$ sudo gedit /etc/apt/sources.list
```

and run `$ sudo apt-get update` to update the sources

then run the following commands:
```
$ sudo apt-get install libttspico0
$ sudo apt-get install libttspico-utils
```

and test that it's all working:

```
pico2wave -w test.wav "it works! "
aplay test.wav
```

#### Flask

create a virtual environment for Flask
```
$ sudo pip install virtualenv
$ mkdir webapp
$ cd webapp
$ virtualenv venv 
```

to activate the environments use `$ . venv/bin/activate`

to exit use `deactivate`

while it is active run this command to install flask

```
$ pip install Flask
```

#### Nginx 

```
sudo apt-get nginx
```

### Ubuntu Server

#### anaconda Python 3

TODO: Optional Intel environment

TODO: create requirement.txt file for python packages

#### CUDA

#### TensorFlow

##### TensorFlow Serving

#### Keras


## Architecture

This project will leverage the computing power of the backend server to process the most expensive tasks and the Raspberry PI hardware for what i call *life support* functions,
in case of communication drops-out with the server i will have the trained models available on the PI in order to provide an emergency backup to fail-safe.

in case the *text to speech* function is too expensive to run on the PI once all the services are running i will review the architecture moving this function to the backend server.

[Architecture]: https://github.com/Drea1989/Odie_robo_assistant/blob/master/architecture%20graph.jpg "Architecture"

![Architecture]


## Components

### Wake on Hotword

Snowboy provided a light and effective hotword detection model, we will train it using our own word 'Odie' the name of the robot.

### Audio / video streaming

Python webservices will provide streaming for video and audio

### Basic Computer Vision

#### Boxes bindings

to avoid latency in the object and face recognition we will use the light OpenCV implementation to find bindings boxes and crop / divide the images to only the parts of interest.

this will avoid to run expensive object recognition models on images without content as well as improve accuracy by subdividing the picture by object contained.


#### image preprocessing

to help navigation we need to preprocess the data by finding edges, removing background and find shapes. the OpenCV pre-built models can quickly prepare the data for DNN capable of driving the robot. this step might be moved to the backend server if the computation is too expensive. 

### Text to speech

i did test multiple open source TTS platforms and voices like Flite and Espeak.

Pico provided the best experience with a more clear pronunciation and less metallic sound. 

### Speech Recognition

#### Artificial Conversational Entity

TODO: Sequence-to-Sequence Models 

based on TensorFlow implementations : lm_1b, SyntaxNet/DRAGNN, textsum

#### speech to text

Mozilla DeepSpeech

### Advanced Computer Vision

#### object recognition

Tensorflow Xception model with transfer learning to train with real life images

considering also TensorFlow object_detection

#### face recognition

DNN architecture based on Xception for face expression and recognition

MMI Facial Expression Database for training and Xception based architecture

#### optical character recognition

DNN based on TensorFlow implementation of attention_ocr

### Interaction DB


#### Users data

SQLScript DB

#### common sentences

TODO: exploring SQL or NO-SQL architecture


### Path Planning

#### face tracking

use camera pan and tilt to keep the face at the centre of the image

#### object following

follow a target object(can be a person) using motion

#### Search

based on TensorFlow implementation of cognitive_mapping_and_planning

### Natural Language Processing

#### words embedding

TODO: Skip-gram Words2Vec

### Decision Making

#### motion controlling

sensor fusion

#### camera controlling

pan/tilt controller

#### command comprehension

task understanding

#### chatting

create user DB

#### fail safe conversations

save conversations and audio/video files to enhancements DB

### Enhancements DB

#### training examples

fill new training examples

#### failed detections

failed interactions


