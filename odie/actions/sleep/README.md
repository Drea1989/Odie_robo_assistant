# sleep

## Synopsis

This action sleeps the system for a given time in seconds.

## Installation

CORE ACTION: No installation needed.  

## Options

| parameter | required | default | choices | comment                         |
| --------- | -------- | ------- | ------- | ------------------------------- |
| seconds   | YES      |         |         | The number of seconds to sleep. |

## Return Values

No returned values

## Synapses example

Simple example : 

```yml
  - name: "run-simple-sleep"
    cues:
      - order: "Wait for me "
    actions:
      - sleep:
          seconds: 60
```


## Notes

