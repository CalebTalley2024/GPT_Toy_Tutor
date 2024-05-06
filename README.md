# Installation
- Install libraries by using `pip install requirements.txt`
- put the .env file in the `command_line_toy` folder

## Workflow
- Edit in Jupiter Notebooks (`.ipynb`), Export the file as a Python (`.py`) file 
### Files: py/ipynb
  - `learning`: code used for teaching student and/or GPT
  - `students`: handles MongoDB database and local Student Objects 
  - `memory`: handles MongoDB database and local MemPropmt Objects
  - `database_connect.py`: connects project to MongoDB database
  - `data_preprocessing.ipynb`: preprocesses subtopics into format identical to `subtopics.csv`
### Data
  - `GPT_tutor_topics(subtopics_included)`: math data
  - `subtopics.csv`: math data preprocessed
# User
  - GPT gives students questions
## Trainer
  - Train GPT Tutors External Databases

# What's Next?
### Reinforcement Learning
  - Neural UCB 
### Robustness Testing
  - Different topics
  - Program synthesis section
  - MemPrompt feedback effectiveness


# Sources
- [sauxpa's implementation of Neural UCB](https://github.com/sauxpa/neural_exploration/blob/master/NeuralUCB.ipynb)
- Rest of sources are in Paper in APA 7 format