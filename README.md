## Iteration 4: MemPrompt
- (after Meeting 2)
### Current Problems
#### Questions
- Writing nothing gets you too high of a score
#### Errors
- the database update fails if the user visits the application multiple times
##### Examples of GPT reasoning errors
- "example Given a triangle with side lengths of 5, 6, and 7 units. Explain how you got your answer."
  - name: Jake
  - topic: "Properties of triangles, quadrilaterals, and other polygons",
  - question is not clear
	- "Example: Bob has 5 apples. How many apples does Alice have?"
- wrong if you get question right, but your reasoning is off
  - `Therefore, the correct answer is x = 4. The student incorrectly stated that 8/2 = 4, which is not true. The correct simplification is 8/2 = 4.`
-  Incorrect multiplication ($0.92 ^ 6$)
   ![[Pasted image 20230728182935.png]]

### Resources used
- [[Research Paper Notes]]
- [Open Source Code Interpreter](https://github.com/shroominic/codeinterpreter-api)
#### Videos
- https://www.youtube.com/watch?v=Ey81KfQ3PQU&ab_channel=JamesBriggs
- inspiration for using python to do the math: https://www.youtube.com/watch?v=1JJqYyNJEeI&ab_channel=TowardstheSingularity
-
#### How papers could be implemented
#### Self Reliance
#### TTRS
- Mathematical Proofs
- Short Answers
- Highlighting core mistake in []
#### MemPrompt
- general arthitecture
	- think about ading a way for having multiple feedback for a question
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
### General Questions
- will this app be used in multiple languages ( ex. African languages like Somali, Amharic, etc )
- ask if it's okay to use `exec`

### Quality of life changes
- flexible formatting for the user ( unlike pearson)
- give the user the chance to ask multiple questions
- confirm button
- try using faster language to convert string to code to solve math
- standardize whether input is just `text` or a `GPT_message`
### Next Step
#### Questions/Answer
- change GPT temperature when asking a question (b/c you don't want to get the same question  with the same prompt)
- Highlight what a students mistakes are in the answer GPT provides
- give students the option to ask questions about the answer GPT gives them
- tailor answers based on mistakes
	- more help for studnets who need more/less help
- if the answer is short, allow no explanation
	- change answer length based on grade and subtopic
		- for basic addition, give brief
#### Students.JSON
- make ID for each student
- make sure that question difficulty changes with level (1-5)
- way for students to confirm answer (takes care of misclicks)
- weighting the evaluation metrics differently

#### Math
- use function calling OR code interpreter open source to do math for GPT, then have GPT explain the answer
	- bad thing: if the python answer is wrong, GPT will make up stuff to show that it's the "right" answer
-  how to make GPT better at arithmetic
	- Figure out way to deal with math when you need to return multiple variables
- Try having GPT double check it's own answer
#### MemPrompt
- What to use to retrieve information
	- sentence transformers?
	- SBERT?
- adding threshold for question_similarity
- order by subtopic instead of by question??
- make question in JSON look better???
### Future Steps
- Use azure cloud as database
- try scheduling meeting with PhD students
- look at paper implementations of the papers read
- ask approxiately when the paper would be done
### Extras
- [Manim Integration](https://github.com/3b1b/manim)
- [Improving Safety](https://twitter.com/aweisawei/status/1677395303773904896)
- Wolfram Alpha LLM integration
- SuperAGI, AutoGPT
- GPT Code Interpreter
- GPT Function Calling