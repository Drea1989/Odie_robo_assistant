# Components

## Wake on Hotword

Snowboy provided a light and effective hotword detection model, we will train it using our own word 'Odie' the name of the robot.

## Audio / video streaming

Python web sockets running on the Pi will provide streaming for video and audio, these will be the inputs for the backend.

## Basic Computer Vision

#### Boxes bindings

to avoid latency in the object and face recognition we will use the light OpenCV implementation to find bindings boxes to pass to the tensorflow model.

this will avoid to run expensive object recognition models on images without content as well as improve accuracy by preprocessing the picture by objects contained.

#### image preprocessing

to help navigation we need to preprocess the data by finding edges, removing background and find shapes. the OpenCV pre-built models can quickly prepare the data for DNN capable of driving the robot. this step might be moved to the backend server if the computation is too expensive. 

## Natural Language Processing

### Text to speech

i did test multiple open source TTS platforms and voices like Flite and Espeak.

Pico TTS provided the best experience with a more clear pronunciation and less metallic sound. 

### Speech Recognition

#### speech to text

i did consider Tensorflow Mozilla DeepSpeech and Neon DeepSpeech2.

Neon was preferred because of the availability of pretrained models and the modern architecture.

#### Words embedding

TODO: Skip-gram Words2Vec

#### Artificial Conversational Entity

TODO: Sequence-to-Sequence Models 

based on TensorFlow implementations : lm_1b, SyntaxNet/DRAGNN, textsum

#### chatting

create user DB where to store information about the people who interacted with Odie, images will be stored with an ID that links to the user in order to train the authentication model.

#### fail safe conversations

we will create a set of neurons that will be triggered in case an action is not understood to log audio/video files into the enhancements DB of the backend server for later improvements.

## Advanced Computer Vision

### Object recognition

Tensorflow Xception model with transfer learning to TensorFlow object_detection,
this model will be compared with the default implementation and the speed/accuracy trade-off will be further analysed. 

#### scenary description

Odie will also provide a brief image caption of what it sees, this will be based on im2txt architecture and implemented in tensorflow.

### face recognition

Xception DNN architecture with learning transfer for face expression and recognition

MMI Facial Expression Database for training and Xception based architecture

### optical character recognition

DNN based on TensorFlow implementation of attention_ocr

## DataBase

### interactions

PostgreSQL is the database of choice because of the free text search capabilites.

### Brain
on initialisation the yaml brain file will be parsed and all the neurons saved into a table.
this table will then be indexed and used to evaluate the STT output to retrieve neurons.

#### Users data

user data and link to profile image ID will be stored for biometric authentication and options customisation. 

#### Non Structured Data

MongoDb is the platform of choice.

commons sentences and enhancement DB will store information on how this data is catalogued to facilitate improvement for later training.

### Enhancements

#### training examples

provide a neuron to trigger save file for less than optimal results, this will have to save neuron id, function called, parameters and audio/video files related to the event to fill new training examples.

#### failed detections

failed interactions

## Path Planning

#### face tracking

use camera pan and tilt to keep the face at the center of the image.

#### object following

follow a target object(can be a person) using motor controlling

#### Search

based on TensorFlow implementation of cognitive_mapping_and_planning

## Rover Controllers

#### motion controller

Motor controller

#### camera controller

pan/tilt servo controller

#### Obstacle Avoidance

sensor fusion

