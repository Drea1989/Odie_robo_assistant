# kill_switch

## Synopsis

This neuron exits the Odie process.

## Installation

CORE NEURON : No installation needed.  

## Options

No parameters

## Return Values

No returned values

## Neuron example

Simple example : 

```yml
  - name: "stop-odie"
    cues:
      - order: "goodbye"
    actions:
      - kill_switch    
```


## Notes

