# Software required and Installation Guide

## Raspberry PI

Install Rasbian NOOBS available [here](https://www.raspberrypi.org/downloads/noobs/) and then proceed with the installation of the software required for the robot to complete it's tasks.

##### Connect to the PI

follow the guides to connect over [VNC](https://www.raspberrypi.org/documentation/remote-access/vnc/) or [SSH - X11](https://www.raspberrypi.org/documentation/remote-access/) for you desktop or laptop to control the PI remotely.

### Install Software

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

### sound card

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

### OpenCV

------

follow the installation guide
[OpenCV Documentation](http://opencv.org/)

pip install "picamera[array]"
sudo apt-get install vlc

### Snowboy

------

follow the installation guide
[Snowboy Documentation](https://snowboy.kitt.ai/)

### Pico TTS

------

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

### Flask

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

### Nginx

```
sudo apt-get nginx
```

## Ubuntu Server

### Anaconda Python 3

TODO: Optional Intel environment

TODO: create requirement.txt file for python packages

### CUDA

### TensorFlow

from source architecture kaby lake

#### TensorFlow Serving

#### Keras

### Neon

