# Odie the RoboAssistant
In this project i will build my first robo assistant, Odie

## Introduction

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

* Rasbian Jessie 8.0

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

#### Flite



#### Nginx 


### Ubuntu Server

#### anaconda Python 3

TODO: Optional Intel environment

TODO: create requirement.txt file for python packages

#### CUDA

#### TensorFlow

#### Keras


## Architecture

This project will leverage the computing power of the backend server to process the most expensive tasks and the Raspberry PI hardware for what i call *life support* functions,
in case of communication drops-out with the server i will have the trained models available on the PI in order to provide an emergency backup to fail-safe.

in case the *text to speech* function is too expensive to run on the PI once all the services are running i will review the architecture moving this function to the backend server.

[Architecture]: https://github.com/Drea1989/Odie_robo_assistant/blob/master/architecture%20graph.jpg "Architecture"

![Architecture]


