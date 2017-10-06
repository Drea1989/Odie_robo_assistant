# Neurotimer

## Synopsis

Run a neuron after a delay.

## Installation

CORE action : No installation needed. 

## Options

| parameter            | required | type   | default | choices   | comment                                  |
| -------------------- | -------- | ------ | ------- | --------- | ---------------------------------------- |
| seconds              | NO       | int    |         | value > 0 | Number of second to wait before running the neuron |
| minutes              | NO       | int    |         | value > 0 | Number of minutes to wait before running the neuron |
| hours                | NO       | int    |         | value > 0 | Number of hours to wait before running the neuron |
| neuron               | YES      | string |         |           | Name of the neuron to run after the selected delay |
| forwarded_parameters | NO       | dict   |         |           | dict of parameters that will be passed to the called neuron |

## Return Values

None

## neurons example


**Scenario:** You are used to make a tea and want to know when it's time to remove the bag.
> **You:** remember me to remove the bag of my tea<br>
> **odie:** Alright<br>
> 3 minutes later..<br>
> **odie:** your tea is ready

```yml
- name: "tea-bag"
  cues:
    - order: "remember me to remove the bag of my tea"
  actions:
    - neurotimer:
        minutes: 3
        neuron: "time-over"
    - say:
        message:
          - "Alright"

- name: "time-over"
  cues:
     - order: "no-order-for-this-neuron"
  actions:
    - say:
        message:
          - "your tea is ready" 
```

If your STT engine return integer when capturing a spoken order, you can set the time on the fly.
**Scenario:** You are starting to cook something
> **You:** notify me in 10 minutes<br>
> **odie:** I'll notify you in 10 minutes<br>
> 10 minutes later..<br>
> **odie:** You asked me to notify you

```yml
- name: "timer2"
    cues:
      - order: "notify me in {{ time }} minutes"
    actions:
      - neurotimer:
          minutes: "{{ time }}"
          neuron: "notify"
      - say:
          message:
            - "I'll notify you in {{ time }} minutes"

- name: "notify"
  cues:
     - order: "no-order-for-this-neuron"
  actions:
    - say:
        message:
          - "You asked me to notify you" 
```

Passing argument to the called neuron with the `forwarded_parameters`.
**Scenario:** You want to remember to do something
> **You:** remind me to call mom in 15 minutes<br>
> **odie:** I'll notify you in 15 minutes<br>
> 15 minutes later..<br>
> **odie:** You asked me to remind you to call mom 15 minutes ago
```yml
- name: "remember-neuron"
  cues:
    - order: "remind me to {{ remember }} in {{ time }} minutes"
  actions:
    - neurotimer:
        seconds: "{{ time }}"
        neuron: "remember-todo"
        forwarded_parameters:
          remember: "{{ remember }}"
          seconds: "{{ time }}"
    - say:
        message:
          - "I'll remind you in {{ time }} minutes"

- name: "remember-todo"
  cues:
    - order: "no-order-for-this-neuron"
  actions:
    - say:
        message:
          - "You asked me to remind you to {{ remember }} {{ time }} minutes ago"
```
> **Note:** You can still use the **odie_memory** instead of **forwarded_parameters** but your value will be overridden if you call the same neuron a multiple time.

## Notes

> **Note:** When used from the API, returned value from the launched neuron are lost

> **Note:** Not all STT engine return integer.

> **Note:** You must set at least one timer parameter (seconds or minutes or hours). You can also set them all.