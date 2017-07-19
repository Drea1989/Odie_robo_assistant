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

Details of Software with installation guide can be found [here](https://github.com/Drea1989/Odie_robo_assistant/blob/master/docs/InstallationGuide.md)

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

- __orders__ spoken by the User 
- __events__ from sensors reading or scheduled 

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

high level detail of each component can be found [here](https://github.com/Drea1989/Odie_robo_assistant/blob/master/docs/Components.md)

