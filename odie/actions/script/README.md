# script

## Synopsis

This action runs a script located on the Odie system.

## Installation

CORE ACTION: No installation needed.  

## Options

| parameter | required | default | choices | comment                                  |
| --------- | -------- | ------- | ------- | ---------------------------------------- |
| path      | YES      |         |         | The path of the script to execute.       |
| async     | NO       | FALSE   |         | If True, Odie will not wait for the end of the execution of the script |

## Return Values

Values are only returned by the action if the async mode is set to `False`.

| Name       | Description                              | Type   | sample                        |
| ---------- | ---------------------------------------- | ------ | ----------------------------- |
| output     | The shell output of the command if any. The command "date" will retun "Sun Oct 16 15:50:45 CEST 2016" | string | Sun Oct 16 15:50:45 CEST 2016 |
| returncode | The returned code of the command. Return 0 if the command was succesfuly exectued, else 1 | int    | 0                             |

## Synapses example

Simple example : 
```yml
  - name: "run-simple-script"
    cues:
      - order: "Run the script"
    actions:
      - script:
          path: "/path/to/script.sh"    
```

If the script can take a long time and you don't want to block the Odie process, you can run it in asynchronous mode.
Keep in mind that you cannot get any returned value with this mode.

```yml
  - name: "run-simple-script"
    cues:
      - order: "Run the script"
    actions:
      - script:
          path: "/path/to/script.sh"   
          async: True
```

Make Odie speak out loud the result of the script.
```yml
  - name: "run-script-an-give-output"
    cues:
      - order: "run the script"
    actions:
      - script:
          path: "/path/to/script.sh"   
          say_template: "{{ output }}"
```

Path an argument to the script from your order
```yml
  - name: "run-simple-script-with-input-value"
    cues:
      - order: "Run the script with {{ my_var }}"
    actions:
      - script:
          path: "/path/to/script.sh {{ my_var }}""   
          async: True
```


## Notes

> **Note:** Odie must have the rights to run the script.

> **Note:** Odie can be used to grant access to an user with lower rights ... !

> **Note:** When 'async' flag is used, returned value are lost

