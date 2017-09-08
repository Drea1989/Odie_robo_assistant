# neurotransmitter

## Synopsis

Link neurons together. Call a neuron directly or depending on the captured speech from the user.

## Installation

CORE ACTION: No installation needed.  

## Options

| parameter        | required | default | choices | comment                                  |
| ---------------- | -------- | ------- | ------- | ---------------------------------------- |
| from_answer_link | NO       |         |         | Link a neuron depending on the answer of the user. Contain a list of tuple neuron/answer object |
| direct_link      | NO       |         |         | Direct call to a neuron by the name of this one |
| neuron           | NO       |         |         | Name of the neuron to launch if the captured audio from the STT is present in the answer list |
| answers          | NO       |         |         | List of sentences that are valid for running the attached neuron |
| default          | NO       |         |         | Name of the neuron to launch if the captured audio doesn't match any answers |

## Return Values

None

## neurons example

We call another neuron directly at the end of the first neuron
```yml
- name: "direct-link"
    cues:
      - order: "direct link"
    actions:
      - say:
          message: "I launch directly the neuron number 1"
      - neurotransmitter:
          direct_link: "neuron-1"

  - name: "neuron-1"
    cues:
      - order: "neuron-direct-link-1"
    actions:
      - say:
          message: "neuron 1 launched"
```


Here the neuron will ask the user if he likes french fries. If the user answer "yes" or "maybe", he will be redirected to the neuron2 that say something.
If the user answer no, he will be redirected to another neuron that say something else.
If the user say something that is not present in `answers`, he will be redirected to the neuron4.

```yml
 - name: "neuron1"
    cues:
      - order: "ask me a question"
    actions:
      - say:
          message: "do you like french fries?"
      - neurotransmitter:
          from_answer_link:
            - neuron: "neuron2"
              answers:
                - "absolutely"
                - "maybe"
            - neuron: "neuron3"
              answers:
                - "no at all"
          default: "neuron4"

  - name: "neuron2"
    cues:
      - order: "neuron2"
    actions:
      - say:
          message: "You like french fries!! Me too! I suppose..."

  - name: "neuron3"
    cues:
      - order: "neuron3"
    actions:
      - say:
          message: "You don't like french fries. It's ok."
      
  - name: "neuron4"
    cues:
      - order: "neuron4"
    actions:
      - say:
          message: "I haven't understood your answer"
```


Neurotransmitter also uses parameters in answers. You can provide parameters to your answers so they can be used by the neuron you are about to launch.
/!\ The params defined in answers must match with the expected "args" params in the target neuron, otherwise an error is raised.

```yml
  - name: "neuron5"
    cues:
      - order: "give me the weather"
    actions:
      - say:
          message: "which town ?"
      - neurotransmitter:
          from_answer_link:
            - neuron: "neuron6"
              answers:
                - "the weather in {{ location }}"

  - name: "neuron6"
    cues:
      - order: "What is the weather in {{ location }}"
    actions:
      - openweathermap:
          api_key: "your-api"
          lang: "fr"
          temp_unit: "celsius"
          country: "FR"
          location: "{{ location }}"
          say_template:
          - "Today in {{ location }} the weather is {{ weather_today }} with {{ temp_today_temp }} celsius"
```

## Notes
> When using the neuron neurotransmitter, you must set a `direct_link` or a `from_answer_link`, no both at the same time.

