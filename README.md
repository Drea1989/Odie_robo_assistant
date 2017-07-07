# Odie the Robotic Assistant

In this project i will build my first robo assistant, Odie

## Introduction

This build includes Open Source products created by 3rd parties, leverage existing solutions makes the product more robust and speeds up the implementation, there is no need to reinvent the wheel.

### Author
Andrea Balzano, AI Engineer with background in computer science and physics.

### Project goals
create a robo-assistant using Raspberry PI, it's features will be built-up step by step increasing scope and complexity as it goes.

this documentation includes both hardware and software implementation.

the hardware is mostly made of plug and play kits since the scope of the build is the AI that controls the robot's functions.

# hardware

#### Notes on the Hardware

the Alphabot 2 for PI turned out to be not the best option for the chassis of the rover, it is very small with littler room for the additional component needed and it is powered by only 2 batteries, insufficient to power the PI, the sensors and the motors, I will work on adding a trailer to carry the extra battery pack as I suggest to look for a different chassis.

### Components

* Raspberry PI 3
* Alphabot 2 for PI
* Raspberry PI camera
* usb sound card
* 3.5mm jack microphone
* 3.5mm jack speaker
* HC-SR04 sonar sensors
* battery Pack
* Backend Server

# Software

### OS supported

this build is designed for the following OS:

Raspberry PI

* Rasbian 8.0 Jessie

Backend Server

* Ubuntu 16.04

## Software required and Installation Guide

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

#### sound card

lookup the audio devices with `aplay -l`

All we need to do is update the sound card index in the Alsa configuration. Open `alsa.conf` with
```
sudo nano /usr/share/alsa/alsa.conf
```

and replace the card number in these lines :

```
defaults.ctl.card 0
defaults.pcm.card 0
```

like these :

```
defaults.ctl.card 1
defaults.pcm.card 1
```
then `reboot`

test the audio `speaker-test -c2 -twav` when you are ready to stop it `ctrl+c` 

to change levels use `alsamixer`

```
sudo apt-get install mplayer2
```

#### OpenCV
------
follow the installation guide
[OpenCV Documentation](http://opencv.org/)

pip install "picamera[array]"
sudo apt-get install vlc

#### Snowboy
------
follow the installation guide
[Snowboy Documentation](https://snowboy.kitt.ai/)

#### Pico TTS
---

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
mplayer test.wav
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
from source architecture kaby lake

##### TensorFlow Serving

#### Keras

### Neon

# Architecture

This project will leverage the computing power of the backend server to process the most expensive tasks and the Raspberry PI hardware for what i call *life support* functions,
in case of communication drops-out with the server i will have the trained models available on the PI in order to provide an emergency backup to fail-safe.

in case the *text to speech* function is too expensive to run on the PI once all the services are running i will review the architecture moving this function to the backend server.

![Architecture](https://github.com/Drea1989/Odie_robo_assistant/blob/master/images/architecture%20graph.jpg)

## Brain

Odie's brain is created with a modular architecture, configuration files will be created in YAML format.

the Brain module loads all the configuration files (Neurons) at startup in the brain.yml file with the following syntax:

```YAML
  - includes:
      - path/to/sub_brain.yml
      - path/to/another_sub_brain.yml
```

the main unit in the brain is the neuron.

each neuron can accept these signals as input:

- _orders_ spoken by the User 
- _events_ from sensors reading or scheduled 

and performs one or more tasks, _brain functions_.

below an example:

```YAML
  - Neuron: "Say-hello"
    triggers:
      - order: "say hello"
    functions:      
      - say:
          message: "Hello, sir"    
```

in detail:

**Neuron** is the Unique ID of the Neuron, It only accepts alphanumeric and dash.

**triggers** is the list of input actions. Any of the signals will trigger the set of output actions.

**functions** are the modules that will be executed when the input action is triggered. 
More than one function can be triggered by the same input action.
This declaration contains a list (because it starts with a "-") of functions

The order of execution is defined by the order in which they are listed in functions declaration.

Some functions need parameters that can be passed as arguments following the syntax below:

```YAML
functions:
    - function_name:
        parameter1: "value1"
        parameter2: "value2"
```

## Components

high level detail of each component can be found [here](C:\Users\andre\OneDrive\RoboAssistant\Docs\Components.md)

