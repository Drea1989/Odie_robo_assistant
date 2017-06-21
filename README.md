# RoboAssistant
---

## Introduction

### Author
---
 
Andrea Balzano, AI Engineer with background in computer science and physics.

### Project goals
------
create a robo-assistant using Raspberry PI, it's features will be built-up step by step increasing scope and complexity as it goes.

this documentation includes both hardware and software implementation.

the hardware is mostly made of plug and play kits since the scope of the build is the AI that controls the robot's functions.

### hardware components
------
* Raspberry PI 3
* Alphabot 2 for PI
* Raspberry PI camera
* sonar sensors
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
------
Install Rasbian NOOBS available [here](https://www.raspberrypi.org/downloads/noobs/) and then proceed with the installation of the software required for the robot to complete it's tasks.

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
`$ sudo apt-get install build-essential git cmake pkg-config`
image I/O packages which allow us to load image file formats such as JPEG, PNG, TIFF, etc.. and then the video I/O packages.
These packages allow us to load various video file formats as well as work with video streams:

```
$ sudo apt-get install libjpeg-dev libtiff5-dev libjasper-dev libpng12-dev
$ sudo apt-get install libavcodec-dev libavformat-dev libswscale-dev libv4l-dev
$ sudo apt-get install libxvidcore-dev libx264-dev
```
We need to install the GTK development library so we can compile the `highgui`  sub-module of OpenCV, which allows us to display images to our screen and build simple GUI interfaces:
`$ sudo apt-get install libgtk2.0-dev`

and follow the guides to connect over VNC or SSH - X11 for you desktop or laptop to control the PI remotely.

follow the guides to complete this tasks

TODO: add link to guide.

#### OpenCV
------
follow the installation guide
[OpenCV Documentation](http://opencv.org/)

### Snowboy
------
follow the installation guide
[Snowboy Documentation](https://snowboy.kitt.ai/)

## Architecture

This project will leverage the computing power of the backend server to process the most expensive tasks and the Raspberry PI hardware for what i call *life support* functions as per graph below

![alt text](C:\Users\andre\OneDrive\RoboAssistant\architecturegraph.jpg "Architecture")
