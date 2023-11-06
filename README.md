## Iteration 4: MemPrompt
- (after Meeting 2)
### Current Problems
- answers for short questions can still have too high of a standard for explanations
#### Questions
- Writing nothing gets you too high of a score
#### Errors
- time error
##### Examples of GPT reasoning errors
- "example Given a triangle with side lengths of 5, 6, and 7 units. Explain how you got your answer."
  - name: Jake
  - topic: "Properties of triangles, quadrilaterals, and other polygons",
  - question is not clear
	- "Example: Bob has 5 apples. How many apples does Alice have?"
- wrong if you get question right, but your reasoning is off
  - `Therefore, the correct answer is x = 4. The student incorrectly stated that 8/2 = 4, which is not true. The correct simplification is 8/2 = 4.`


### Resources used
- [[Research Paper Notes]]
- [Open Source Code Interpreter](https://github.com/shroominic/codeinterpreter-api)
#### Videos
- https://www.youtube.com/watch?v=Ey81KfQ3PQU&ab_channel=JamesBriggs
- inspiration for using python to do the math: https://www.youtube.com/watch?v=1JJqYyNJEeI&ab_channel=TowardstheSingularity
-
#### How papers could be implemented
##### Self Reliance
##### TTRS
- Mathematical Proofs
- Short Answers
- Highlighting core mistake in []
##### MemPrompt
- general architecture
	- think about adding a way for having multiple feedback for a question
- basic math logic
-

#### Possibly relevant papers
- https://twitter.com/Ber18791531/status/1685361949230436352

### Web Iteration
- Svelte + FastAPI: https://github.com/OriginalStefikO/fastapi-svelte-starter
  - Webstorm vs VScode
  - Tailwind
  - tools
      - front end: SVelte
          - HTML
          - CSS
          - Javascript??
      - backend
          - FastAPI
          - server: Uvicorn
          - 
### General Questions
- will this app be used in multiple languages ( ex. African languages like Somali, Amharic, etc )
- ask if it's okay to use `exec`
  - [Be Careful When Using exec() or eval() in Python - YouTube.url](https://www.youtube.com/watch?v=keSvLnLNep4&ab_channel=NeuralNine)

### Quality of life changes
- confirm button
- try using faster language to convert string to code to solve math
- string to python has to have specific syntax

### Next Step

#### Questions/Answer
- Highlight what a students mistakes are in the answer GPT provides
- tailor answers based on mistakes
	- more help for students who need more/less help
- if the answer is short, allow no explanation
	- change answer length based on grade and subtopic
		- for basic addition, give brief
- add mem prompt to student learning?
- Try having GPT double check it's own answer ( using python)
- make sure that question difficulty changes with level (1-5)
#### Students.JSON
- make ID for each student
- way for students to confirm answer (takes care of miss clicks)
- weighting the evaluation metrics differently

#### Math
- use function calling OR code interpreter open source to do math for GPT, then have GPT explain the answer
	- bad thing: if the python answer is wrong, GPT will make up stuff to show that it's the "right" answer
-  how to make GPT better at arithmetic
	- Figure out way to deal with math when you need to return multiple variables
   - Self Refine process for the python 
- fix grading shortcuts
  - " the answer is "x" because that's how math works" gets too high of a score

#### MemPrompt
- What to use to retrieve information
	- sentence transformers?
	- SBERT?
- adding threshold for question_similarity
- order by subtopic instead of by question??
- make question in JSON look better???
- Trying to use Self Refinement to check code?
  - if so, try different temperatures pertaining to code review
### Future Steps
- Use azure cloud as database
- Expand into a Test
- try scheduling meeting with PhD students
- look at paper implementations of the papers read
- ask approxiately when the paper would be done
- When deploying project, CHANGE/Remove/Secure GPT API key
### Extras
- [Manim Integration](https://github.com/3b1b/manim)
- [Improving Safety](https://twitter.com/aweisawei/status/1677395303773904896)
- [I built my own AutoGPT that makes videos](https://youtu.be/_rGXIXyNqpk)
- Wolfram Alpha LLM integration
- SuperAGI, AutoGPT
- GPT Code Interpreter
- GPT Function Calling
- DJango
- Docker
- Gorilla AI

## Iteration 5: MongoDB
- Now have MongoDB database for storing memory
- Added OOP for memorys\

### Issues

#### Extremely Minor/ Neglibible
- having way to deal with name conflicts ( unlikely now because we are using a student's full name as opposed to just first name)

### Things to remember
- tighten security for MongoDB for deployment if necessary