# kill_switch

## Synopsis

This neuron exits the odie process.

## Installation

CORE NEURON : No installation needed.  

## Options

No parameters

## Return Values

No returned values

## Synapses example

Simple example : 

```yml
  - name: "stop-odie"
    cues:
      - order: "goodbye"
    actions:
      - kill_switch    
```


## Notes

