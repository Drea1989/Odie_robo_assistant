# Caption

## Synopsis

This action take a picture with picamera and predicts a caption for it.

## Installation

CORE ACTION: No installation needed.  

## Options

| parameter | required | default | choices | comment |
| --------- | -------- | ------- | ------- | ------- |
| None      |          |         |         |         |

## Return Values

Values are only returned by the action if the async mode is set to `False`.

| Name       | Description                              | Type   | sample                        |
| ---------- | ---------------------------------------- | ------ | ----------------------------- |
| output     | The shell output of the command if any. The command "date" will retun "Sun Oct 16 15:50:45 CEST 2016" | string | Sun Oct 16 15:50:45 CEST 2016 |
| returncode | The returned code of the command. Return 0 if the command was succesfuly exectued, else 1 | int    | 0                             |

## Neurons example

Simple example : 
```yml
  - name: "caption-this"
    cues:
      - order: "what do you see"
    actions:
      - caption:
```


## Notes

> **Note:** Odie must have picamera

