# say

## Synopsis

This action is the mouth of odie and uses the [TTS](../../Docs/tts.md) to say the given message.

## Installation

CORE ACTION: No installation needed.  

## Options

| parameter | required | default | choices | comment                           |
| --------- | -------- | ------- | ------- | --------------------------------- |
| message   | YES      |         |         | A list of messages odie could say |

## Return Values

No returned values

## Synapses example

Simple example : 

```yml
- name: "Say-hello"
  cues:
    - order: "hello"
  actions:
    - say:
        message:
          - "Hello Sir"     
```

With a multiple choice list, odie will pick one randomly:

```yml
- name: "Say-hello"
  cues:
    - order: "hello"
  actions:
    - say:
        message:
          - "Hello Sir"
          - "Welcome Sir"
          - "Good morning Sir"
```

With an input value
```yml
- name: "Say-hello-to-friend"
  cues:
    - order: "say hello to {{ friend_name }}"
  actions:
    - say:
        message:
          - "Hello {{ friend_name }}"     
```

## Notes

> **Note:** The action does not return any values.
> **Note:** odie randomly takes a message from the list 
