#!/usr/bin/env python
# coding: utf-8

# In[1]:


from dotenv import load_dotenv
#TODO use dotenv file when you release final version
import json
import openai
import os
import numpy as np
import pandas as pd
import time

# import custom python files for memory and students functions
import Memory
import students


# In[2]:


# get syllabus
# df1 = pd.read_csv('topics.csv')
df2 = pd.read_csv('../data/GPT_tutor_topics(sub_topics_included).csv')
# df2


# In[3]:


load_dotenv()


# get key and model
openai.api_key = os.getenv('OPENAI_KEY_1')
# openai.api_key = "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"
model_35 = "gpt-3.5-turbo"
student_data_path = "../data/students.json"
memory_path = "../data/memory.json"
question_temp = 1 # temp has to be between 0 and 2


# In[3]:





# In[4]:


# data helper functions for JSON data

# getting external data
def get_ext_data(path):
    with open(path, "r") as file:
        database = json.load(file)
    return database

# post/update at the external data path
def post_ext_data(data, path):
    with open(path, 'w') as f:
        json.dump(data, f, indent=4)


# In[5]:


# helper functions

# API responses
def get_response(messages):
    res = openai.ChatCompletion.create(
        model = model_35,
        messages = messages,
        temperature = 0 # make sure responses are deterministic/consistent
    )
    return res
def get_response_text(messages):
    res = get_response(messages)
    return res['choices'][0]['message']['content']
# be able to get the response and edit temperature
def get_response_text_w_temp(messages, temp):
    res = openai.ChatCompletion.create(
        model = model_35,
        messages = messages,
        temperature = temp # make sure responses are deterministic/consistent
    )
    return res['choices'][0]['message']['content']


# In[6]:


# creates one part of the message that you send to the GPT API for a response.
# add brackets [] if you want to use this function to make a full message
# System: 1
# Assistant: 2
# User: 3
def create_message_part(text, role_type):
    role = None
    if role_type == 1:
        role = "system"
    elif role_type == 2:
        role = "assistant"
    elif role_type == 3:
        role = "user"

    message_part = {
        "role": role,
        "content": text
    }

    return message_part


# In[7]:


# temporary helper functions
def manual_level_reset(name, sub_topic, level):
    # Get data from students.json
    data = get_ext_data(student_data_path)

    # Check if the student is in the database
    students = data['students']
    for student in students:
        if name in student:
            # Check if the student has a section for the given subtopic
            sections = student[name]
            for section in sections:
                if section['sub_topic'] == sub_topic:
                    # Reset the student's metrics
                    section['proficiency_metrics'] = clear_metrics()
                    section['level'] =  level
                    section['questions_answered'] = [0, 0, 0, 0, 0]
                    print(f"{name}'s data metrics for '{sub_topic}' has been reset.")
                    break
    print("level changed, database stats reset")
    # Write the updated data back to students.json
    post_ext_data(data, student_data_path)


# In[8]:


def get_student_subtopic_level(student, sub_topic):
    # Read the JSON file
    data = get_ext_data(student_data_path)

    # if we don't find the student, or the subtopic in the database, we will use the lowest level by default
    default_level = 1

    # Access the student's data from the database
    student_data = None
    for student_entry in data["students"]:
        if student in student_entry:
            student_data = student_entry[student]
            break

    if student_data is not None:
        # Find the sub-topic information for the student
        sub_topic_data = None
        for entry in student_data:
            if entry["sub_topic"] == sub_topic:
                sub_topic_data = entry
                break

    # Check if student exists in the database
    if student_data is None:
        print("student is not in database. They will be start at Level 1, Proficiency 1")
        return default_level
    # Check if sub-topic exists for the student
    if sub_topic_data is None:
        print(f"student has no data for '{sub_topic}' in this database. They will be start at Level 1.")
        return default_level
    else:
        # Retrieve the level and proficiency scores
        level = sub_topic_data["level"]

    # Return the level and proficiency scores
    return level


# In[9]:


# helper functions for ask_question
# database is currently 'students.json'
# 1. make sure GPT only answers math questions
def filter_answers():
    message = {
        "role": "system",
        "content": f"I am a math teacher for Grade K-12 in the United States. I am using the GPT API to help me answer my students' math questions. Please only answer my questions about math, and do not respond to any questions that are not about math."
    }
    return message
# is_current_student: boolean
def init_question(student, subtopic, user_type):

    # Prompt for level choice
    if user_type == "user":
        print("Hello User/Student! \npicking the level manually will only affect the type of questions you get")
        choice = input("Do you want to pick the level? (Y/N): ")
    elif user_type == "trainer":
        print("Hello Trainer. \n Since you are training GPT_Tutor, you will be able to pick the level of the question that you get")
        choice = "Y"
    else:
        print("Invalid input")

    # If statement based on the choice
    if choice.upper() == "Y":
        valid = True
        while valid:
                custom_level = int(input("Enter the level you want between 1 and 5: "))
                if custom_level > 5 or custom_level < 1:
                    print("Invalid level, pick again.")
                else:
                    valid = False
                    # Reset student's level if needed
                    subtopic.level = custom_level
                
    # criteria: tell GPT scales for proficiency and level
    init = f"Based on {student}'s database, the student's skill level for {subtopic.name} is {subtopic.level}. Please give {student} a test question based on {subtopic.name} and follow up with a sentence like 'Explain how you got your answer'. Adjust the difficulty of the question based on his skill level and proficiency score. DO NOT include any other words. Do not put the answer in the prompt."
    criteria = f"Level is on a scale between 1 and 5, where 5 is the hardest level."

    # combine criteria and message
    message = f"{init} {criteria}"
    init_crit = create_message_part(message,1) # create system message

    return init_crit
# changes the format of the question GPT gives
def question_formatting():
    init = """
    This is the format that you should be using

    """
    format = """
        Level 1 (Difficulty: Easy):
        Subtract the following without regrouping (no borrowing):

        1. 46-19

    """
    level_meaning = """
    Remember the description that follows each Level

    Level 1 (Difficulty: Easy):

    Level 2 (Difficulty: Easy-Moderate):

    Level 3 (Difficulty: Moderate):

    Level 4 (Difficulty: Moderate-Hard):
    Level 4 (Difficulty: Hard):

    """
    formatting =  {
            "role": "system",
            "content": f"{init},{format}"
        }

    level_meaning = {
            "role": "assistant",
            "content": level_meaning
        }



    return formatting, level_meaning


# In[10]:


# ask question to student
def ask_question(student, sub_topic, user_type):
    # make sure to only receive math answers and initialize the questions GPT will give
    filter_subject = filter_answers()
    filter_question = init_question(student, sub_topic,user_type)
    formatting, level_meaning = question_formatting()
    messages = [filter_subject, filter_question, formatting, level_meaning]
    # print(messages)
    # send the formatting to GPT and get a response
    tutor_question = get_response_text_w_temp(messages,question_temp)
    # here we print out the question GPT gives the student
    print(f"{tutor_question}: \n\n")
    # make sure the question is always in lower case
    tutor_question = tutor_question.lower()
    return tutor_question


# In[10]:





# In[11]:


# ask_question("Alice", "2 digit division","user") #test


# In[12]:


# time: time it took the student to answer the question given from GPT
# returns
#   - the response the student gives
#   - the time it takes to get a response form the student
def get_student_timed_response():
    start_time = time.time()

    student_res = input() # response to question

    end_time =  time.time()
    end_time = end_time - start_time

    return student_res, end_time


# In[13]:


def respond_to_student_ans(question, student_answer, student_name,gpt_ans_explanation,get_all_student_related_mistakes):
    # take in the student_name's answer, and the topic
    print("Answer: \n")
    question_message = {
        "role": "system",
        "content": f"You are a math tutor. The question that the user is answering is '{question}'."

    }
    answer_explained = {
        "role": "user",
        "content": f"The GPT answer that you have found is derived below: \n{gpt_ans_explanation}\n\n{student_name}'s answer is {student_answer}. Tell whether the student got the question correct based on the GPT answer and give and provide an explanation of the correct answer. Also explain where the student is incorrect"
    }

    use_student_mistakes = {
        "role": "user",
        "content": f" These are the mistakes that {student_name} made while doing these types of problems: {get_all_student_related_mistakes}. in your answer. high light how he has improved on his mistakes,and/or how he is still doing the same mistake. If the studnet does not currently have any related mistakes, dont mention anything about related mistakes"
    }
    init_response_messages = [question_message,answer_explained,use_student_mistakes]

    answer_res = get_response_text(init_response_messages)

    print(f"{answer_res}\n\n")

    return answer_res

def grade_student_response(question, student_answer, student_name,solve_time, sub_topic,answer_res):

    print("Evaluation: \n")
    # if the question being asked is simple we want to make sure the user does not have to give an explanation if non is needed
    # here are examples of questions that don't need  much explanation
    simple_question_examples = """
    Addition: 2 + 3, 99 + 92
    Subtraction: 10 - 4, 345 - 234
    Multiplication: 5 * 6, 99 * 99
    Division: 20 ÷ 4
    Square of a number: 4**2, 78**2
    Cube of a number: 3**3
    """
    evaluation_messages = [
        {
            "role": "system",
            "content": f"The topic of the question is {sub_topic}. This is the question given to {student_name}: {question}. {student_name}'s answer is {student_answer}. This  is the answer you gave: {answer_res}."
        },
        {
            "role": "system",
            "content": f"This I need you to evaluate {student_name}'s performance in terms of the following skill metrics: communication, interpretation, computation, conceptual, and the time taken to solve the question (it took the student {solve_time} seconds to complete the question. For each of these metrics, rate the skill out of 5, where 5 out of 5 is the best score, and 1 out of 5 is the worst score. make sure to have your evaluation in outline format. Also give an explanation on how {student_name} did not get the highest marks. Make sure to use Integers, NOT decimals "
        },
        {
            "role": "system",
            "content": f"if the question being asked is brief and does not require much of an explanation, automatically give the student a 5 out of 5 score for communication. The following are examples of questions that dont require the student to give a long explanation: {simple_question_examples}. for all questions similar to this, the metric score for communication will always be 5."

        },
        {
            "role": "system",
            "content": " if you cannot find any related mistakes for a metric, automatically give a score of 5 for the corresponding metric"
        },
        {
            "role": "system",
            "content": "at the end, give an average score based on the above metrics"
        },
        {
            "role": "system",
            "content": "make sure that you always have a time metric"
        }
    ]
    evaluation_res = get_response_text(evaluation_messages)
    print(evaluation_res)
    print(" \n\n")
    metrics_scores = extract_metrics_scores(evaluation_res)

    # print(metrics_scores)
    return  metrics_scores



# In[14]:


# give students the ability to ask for clarification regarding a question they have about the answer to the question
def get_gpt_clarification (question, gpt_answer, student_answer, previous_explanations):
    # ask the student if they need clarification on a question.
    # if they do. give them a chance to ask the question
    # if they dont, then dont provide anything


    # make sure the response safe and only related to mathematics
    only_answer_math = f'''I am a math teacher for Grade K-12 in the United States. I am using the GPT API to help me answer my students' math questions. Please only answer my questions about math, and do not respond to any questions that are not about math.'''

    only_answer_math_msg = create_message_part(only_answer_math,1)

    previous_info = f"""
    Question: {question},
    GPT's answer ( assume this is correct): {gpt_answer},
    student's answer (this could, or could not be correct){student_answer},
    previous explanations to students questions:{previous_explanations}
    """
    # create system message
    previous_info_msg = create_message_part(previous_info,1)


    # create message for the student's question on the math problem
    student_question = input("Write down what you want clarification on")
    student_question_msg = create_message_part(student_question,3)

    msgs = [only_answer_math_msg,previous_info_msg,student_question_msg]

    GPT_res = get_response_text(msgs)

    print("\n")
    print(GPT_res)

    return GPT_res

# GPT gives a detailed explanation given a student's question on the math problem
# ques_explain: math question and the previous student questions asked and the GPT resposes given
def student_clarification(question, gpt_answer, student_answer, previous_explanations):
    # Ask the student if they want clarification about the answers given
    need_clarification = input("If you want clarification, type 'Yes'. Type anything else to got to the evaluation section\n")

    need_clarification = need_clarification.lower()
    if need_clarification == "yes".lower():
        # Get clarification from the student using the get_gpt_clarification function
        new_clarification = get_gpt_clarification(question, gpt_answer, student_answer, previous_explanations)

        # Update previous explanations with the new clarification
        previous_explanations = previous_explanations + "  ,  " + new_clarification

        # Recursive call to continue the clarification process
        student_clarification(question, gpt_answer, student_answer, previous_explanations)
    else:
        print("Student questioning section has been completed.\nNext: Metric scores for performance\n")


# In[15]:


# question = "Solve for x: 2x + 5 = 15"
# gpt_answer = "x = 5"
# student_answer = "x = 6"
# previous_explanations = ""
# student_clarification(question, gpt_answer, student_answer, previous_explanations)


# In[16]:


# gpt_res: evaluation on how the student answered the questions
def extract_metrics_scores(gpt_res): #TODO fix extract_metric scores, the response uses "scores"
    instruction = f'''


    Here is the Evaluation for a certain student. \n\n{gpt_res}\n\n---\n.

    From this evaluation, extract it's evaluation metric numbers and put them in teh shape of a JSON file. 
    
    Answer this question in the form of a JSON file.
    
    Please respond in plain text without using any code formatting like 'json', '```', <string>, etc. 


'''
    # get examples of what should be done.
    example_1_eval = """
        Evaluation of Allan's Performance:

        1. Communication: 4/5
           - Allan effectively communicated his answer and explanation in a clear and concise manner. However, there could have been more elaboration and clarity in his explanation.

        2. Interpretation: 5/5
           - Allan correctly interpreted the given equation and understood the objective of isolating x.

        3. Computation: 5/5
           - Allan correctly performed the necessary computation steps to solve the equation and obtained the correct answer.

        4. Conceptual Understanding: 4/5
           - Allan demonstrated a good understanding of the concept of isolating x in an equation. However, his explanation could have included more conceptual details to further enhance his understanding.

        5. Time Taken: 5/5
           - Allan was able to solve the question in a relatively short amount of time, taking only 20 seconds.

        Average Score: (4 + 5 + 5 + 4 + 5) / 5 = 4.6/5

        Explanation:
        Allan's performance was generally strong across all skill metrics. He effectively communicated his answer and demonstrated a good understanding of the concept. However, his explanation could have been more detailed and comprehensive, which affected his score in the communication and conceptual understanding categories. Overall, Allan performed well and achieved a high average score of 4.6 out of 5.
        """
    # What the function should output
    # TODO: if you are having issues with example_1_res, use the OLD version here
    example_1_res_OLD = """
        {
                {
        "overall_avg": 4.6,
        "communication": {
            "avg_score": 4,
            "related_mistakes": ["could have been more elaboration and clarity in his explanation."]
        },
        "interpretation": {
            "avg_score": 5,
            "related_mistakes": []
        },
        "computation": {
            "avg_score": 5,
            "related_mistakes": []
        },
        "conceptual": {
            "avg_score": 4,
            "related_mistakes": ["explanation could have included more conceptual details to further enhance his understanding"]
        },
        "time": {
            "avg_score": 5,
            "seconds": 20
        }
    }
    }
    """
    # What the function should output
    example_1_res = '''
                {
        "overall_avg": 4.6,
        "communication": {
            "score": 4,
            "related_mistakes": ["could have been more elaboration and clarity in his explanation."]
        },
        "interpretation": {
            "score: 5,
            "related_mistakes": []
        },
        "computation": {
            "score: 5,
            "related_mistakes": []
        },
        "conceptual": {
            "score: 4,
            "related_mistakes": ["explanation could have included more conceptual details to further enhance his understanding"]
        },
        "time": {
            "score: 5,
            "seconds": 20
        }
    }
    '''

    example_2_eval = """
        Evaluation of Alice's Performance:

    1. Communication: 2/5
       - Alice's answer does not clearly explain the steps taken to subtract the numbers.
       - The answer provided is incorrect and does not demonstrate a clear understanding of the subtraction process.

    2. Interpretation: 1/5
       - Alice misinterpreted the question and did not understand that regrouping (borrowing) was not allowed.
       - The answer provided does not align with the given instructions.

    3. Computation: 1/5
       - Alice's answer of 24 is incorrect and does not reflect the correct subtraction calculation.
       - The computation process used by Alice is flawed and does not follow the correct method of subtraction without regrouping.

    4. Conceptual: 1/5
       - Alice lacks a clear understanding of the concept of subtraction without regrouping.
       - The incorrect answer and flawed computation process indicate a lack of conceptual understanding.

    5. Time taken: 5/5
       - Alice completed the question in a reasonable amount of time, indicating a decent level of speed and efficiency.

    Average Score: (2 + 1 + 1 + 1 + 5) / 5 = 2/5

    Explanation:
    Alice's performance in this question is below average. She struggled with communication, interpretation, computation, and conceptual understanding. Her answer was incorrect, and she did not follow the correct method of subtraction without regrouping. Alice needs further practice and clarification on the concept of subtraction to improve her skills in this area.
    """
    example_2_res = """
        {
            "overall_avg": 2,
            "communication": {
                "score": 2,
                "related_mistakes": [" does not clearly explain the steps taken to subtract the numbers."]
            },
            "interpretation": {
                "score": 1,
                "related_mistakes": [misinterpreted the question and did not understand that regrouping (borrowing) was not allowed,The answer provided does not align with the given instructions.]
            },
            "computation": {
                "score": 1,
                "related_mistakes": [does not follow the correct method of subtraction without regrouping.]
            },
            "conceptual": {
                "score": 1,
                "related_mistakes": ["lacks a clear understanding of the concept of subtraction without regrouping"]
            },
            "time": {
                "score": 5,
                "seconds": 20
            }
    }
    """
    instruction_msg = create_message_part(instruction,1)
    example_1_res_msg =  create_message_part(example_1_eval,3)
    example_1_res_ans =  create_message_part(example_1_res,2)
    example_2_res_msg =  create_message_part(example_2_eval,3)
    example_2_res_ans =  create_message_part(example_2_res,2)

    # add instructions and examples to messages
    messages = [instruction_msg, example_1_res_msg, example_1_res_ans,example_2_res_msg,example_2_res_ans]

    # get JSON data in form of response string
    metric_scores_string = get_response_text_w_temp(messages,0) # temp  = 0

    # make the string a JSON
    # print(f"\nMetrics_scores_string {metric_scores_string} \n")

    metric_scores_json = eval(metric_scores_string)
    return metric_scores_json

    # # print(metric_scores_json)
    # return metric_scores_string


# In[17]:


# question: String
# student, sub_topic: custom Objects
# all_student_subtopic_mistakes: dictionary
# receive student's answer, respond to their answer, and update their statistics
def receive_respond_and_update(question, student, sub_topic, all_student_subtopic_mistakes):
    # Get the student's response and the time taken
    student_answer, solve_time = get_student_timed_response()

    # Grade the student's response using the given question, student response, time, and sub_topic

    # get the answer + explanation that GPT provides with python doing the math.
    # uses "memPrompt" like memory
    gpt_ans_explanation, _ = get_answer_explanation_with_memory(question)

    answer_res = respond_to_student_ans(question, student_answer, student.name, gpt_ans_explanation,all_student_subtopic_mistakes)

    previous_explanations = " " # we start the previous explanations empty
    student_clarification(question,answer_res,student_answer,previous_explanations)
    gpt_res = grade_student_response(question, student_answer, student.name, solve_time, sub_topic.name,answer_res)

    # Extract metric updates from the GPT response
    metric_updates = extract_metrics_scores(gpt_res)

    # Return the metric updates
    return metric_updates


# In[41]:


#TODO make a test portion
#TODO Evaluating AI/Student's Answer to question


# In[22]:


# converts question's format into python formatting
def question_python_notation(question):
    system_text = """
    make the following questions in python notation:

    Here is an example"

    User: "What is 0.9^6" in python notation

    Assistant: "What is 0.9**6"

    User: "What is 0.9 raised to the power of 6" in python notation

    Assistant: "What is 0.9**6"


    """
    prompt_text = question
    system_msg = create_message_part(system_text,1)
    prompt_msg = create_message_part(prompt_text,3)
    messages = [system_msg,prompt_msg]
    converted_notation = get_response_text(messages)
    # print( converted_notation)
    return  converted_notation

# using question given and answer given in python, make GPT backtrack to find a solution that gets the answer
def backtrack_to_explanation(question, answer):
    # to make sure that are answers are accurate and consistant, we make sure that GPT receives the answers in python notation
    converted_question = question_python_notation(question)

    system_text = "You will be given a question, and an answer to a question. It is your job to explain the correct way how to get from the question to the answer step by step.  "
    prompt_text = f"the question is {converted_question}, the answer is {answer}"

    system_msg = create_message_part(system_text,1)
    prompt_msg = create_message_part(prompt_text,3)

    messages = [system_msg,prompt_msg]
    explanation = get_response_text(messages)
    print(explanation)
    return explanation


# In[23]:


#### TRYING TO run python code to get question right
def question_to_code_block(question):
    message = [
        {
            # the code needed for "exec" to work need specific formatting
            # make sure GPT will only give answers that are executable in python
            "role": "system",
            "content": """
            When asked anything, the answer will always be in python code, using a function. no other comments. make sure to call the function

            Example

            user: what is 0.9**6

            assistant:

            def test()
                value = 0.9**6
                ans = f"the answer to the question is {value}"
                return ans
            result = test() # MAKE SURE TO INCLUDE THE 'result = <function()>'
            """
            # "When asked anything, the answer will always be in python code, using a function. no other comments. use a print statement when calling the function"
            # "When asked anything, the answer will always be in python code, using a function. no other comments, You are allowed to use external libraries such as numpy, scipy, etc"

            # "When asked anything, the answer will always be in python code. no other comments, just python code. make sure the return is in a print statement"
        },
        {
            "role": "system",
            "content": question
        }

    ]
    code_block = get_response_text(message)
    return code_block
# This function takes a code block as input and returns the value given when the python code is executed

#TODO the use of "exec could possible be a security risk
def code_block_to_variable(code_block):
    # Create an empty dictionary to store the variables that are created in the executed code.
    data = {}

    # Execute the code block and store the results in the dictionary `data`.
    exec(code_block, None, data)

    # Get the value of the variable `result` from the dictionary `data`.
    var = data["result"]

    return var

def solve_simple_math(question):
    code_block = question_to_code_block(question)
    print(f"python code: {code_block}")
    ans = code_block_to_variable(code_block)
    # convert answer into string
    print(f"answer: {ans}")
    return ans

def explain_simple_math(question):
    ans = solve_simple_math(question)
    # print(f" this is {str(ans)}")
    explanation = backtrack_to_explanation(question,ans)
    # return explanation
    return ans

#TODO Self Refine
def self_refine_answer(question, answer): # based on "Self Refine" paper
    # set up th question and answer so that GPT the reflect on it's own code
    set_up_question = f"Here is the following question: {question}\n"
    set_up_answer = f'''

    Here is the python code that lead to an answer I was previously {answer}

    '''
    instructions = '''If one exists, identify the error in the code and refine the solution through an iterative process of introspection and feedback'''

    question_msg = create_message_part(set_up_question,1)
    answer_msg = create_message_part(set_up_answer,1)
    instruction_msg = create_message_part(set_up_question,3)

    messages = [question_msg,answer_msg,instruction_msg]

    res = get_response_text(messages)

    pass
#TODO update memPropmt and studnet_learning to include Self_Refine



# In[24]:


q1 = "What is 0.96**5"
q2 = "If x + y = 0, and y + 2 = 24, what are x and y"
q3 = "What is the derivative of  ln(x) with respect to x"
q4 = '''
Twenty dozen cups cost $1200 less than the total cost of
half a dozen plates sold at $6000 each.
Calculate the total cost of buying each cup.
''' # Example from Self Reliant Paper

# code_b = question_to_code_block()
# code_b
#
# ans1 = solve_simple_math(code_b)

# explain_simple_math(q1)



# 
# 

# In[25]:


# 0.96**5


# In[26]:


# query = "Calculate the area of a rectangle with length 5 and width 8."
# Memory.find_most_similar_memory(query)


# In[27]:


# creates prompt with question and feedback if it exists
def create_prompt(question, feedback):
    # make the question and feedback into one prompt
    question_msg = create_message_part(question,3)

    set_up_msg = "user feedback:"
    prepare_for_feedback = create_message_part(set_up_msg,3)

    # feedback is given by the system
    feedback_msg = create_message_part(feedback,1)

    show_explanation = "make sure to explain how you got to your answer"
    show_explanation_msg = create_message_part(show_explanation,1)

    prompt = [question_msg, prepare_for_feedback, feedback_msg,show_explanation_msg]

    return prompt


def get_answer_from_explanation(explained_ans):
    instruction = "From the given explanation, give only the question solved and the answer given"

    instruction_msg = create_message_part(instruction,1)

    explained_ans_msg = create_message_part(explained_ans,3)

    msgs = [instruction_msg,explained_ans_msg]

    ans = get_response_text(msgs)

    return ans

# splits up explained answer into two parts: The answer itself and the explanation that leads to the answer
def get_answer_and_explanation(prompt):

    # generate the explained answer
    explanation = get_response_text(prompt)
    answer = get_answer_from_explanation(explanation)
    return explanation, answer


# give user feedback to perosn
def send_feedback(question, feedback):
    # get the Memory.json data
    data = get_ext_data(memory_path)
    # Search for the question in the database
    found_question = False

    for entry in data:
        if entry["Question"] == question:
            # Add the feedback to the existing entry
            print(entry["Feedback"])
            entry["Feedback"].append(feedback)
            found_question = True
            print("feedback has been added to the question")
            break

    # If the question is not in the database, add a new JSON entry
    if not found_question:
        new_entry = {
            "Question": question,
            "Feedback": [feedback],
        }
        data.append(new_entry)
        print("the question and the feedback has been added to memory")

    # print("Memory database has been updated")


    # update the Memory.json file with the new information
    post_ext_data(data,memory_path)

# will update the memory if the user spots a mistake that GPT has made in the answer and/or the explanation of the answer
def update_memory(question, answer, explanation):
    # first display the answer to the user
    print(f"Answer: {answer}")
    print(f"Explanation: {explanation}\n")
    need_feedback = input("does the answer and explanation above require any feedback: 'Yes', or 'No'")
    if need_feedback == 'Yes':
        feedback = input("What needs to be improved in the analysis process?")
        memories0 = Memory.Memories() # creates Memories Object
        memories0.update_memory_feedback(question, feedback)
    else:
        print("Memory will not be updated")


# In[28]:


# GPT answser the question with the feedback memory json
def get_answer_explanation_with_memory(question):
    # get the feedback associated with the most similar question
    _,similar_feedback = Memory.find_most_similar_memory(question)
    # convert the list to a string
    feedback_str = f"{similar_feedback}"
    # print(type(feedback_str))
    print(f"found feedback from memory.json: {feedback_str}")
    prompt = create_prompt(question,feedback_str)

    # get the GPT generated answer and explanation
    #ans_explanation: gives both the answer to the quesiton and the explanation of the answer
    ans_explanation, answer = get_answer_and_explanation(prompt)
    return ans_explanation,answer


# In[29]:


# based off "MemPrompt: Memory-assisted Prompt Editing with User Feedback" paper
def mem_prompt_learning():
    sub_topic_name = input("Enter the sub-topic you want to learn: ")
    user_type = "trainer"

    # make subtopic and studnet objects we will use just for training
    # nothing will chagne in teh students database collection on MongoDB
    sub_topic_placeholder = students.Subtopic(sub_topic_name,1)
    student_placeholder = students.Student("trainer",1) # placeholder for a student's name. This will NOT negatively affect the ask_question function

    # get the question
    question = ask_question(student_placeholder,sub_topic_placeholder,user_type)
    # find the question, or the most similar question that's in the database already
    # get the GPT generated answer and explanation
    explanation, answer = get_answer_explanation_with_memory(question)

    # update the memory.json file ( if the answer is already correct, then nothing in the database will change)

    update_memory(question, answer, explanation)

    # Ask the student if they want to be asked another question.
    answer = input("Do you want another question? 'yes' or 'no' ")

    answer = answer.lower()
    while answer not in ("yes", "no"):
        answer = input("Invalid input: Please enter 'yes' or 'no': ")

    if answer == "yes":
        mem_prompt_learning()
    else:
        print("Thank you training GPT Tutor! Have a great day.")


# In[30]:



# asks student question, evaluates and updates their database
def student_learning():

    user_type = "user"
    # get students database collection from MongoDB
    main_collection = "Section0"
    StudentCollection = students.StudentsCollection(main_collection)
    all_student_names = StudentCollection.current_student_names()


    """Asks the student a question and updates their stats."""
    full_name = input("Enter your full name (Example: John Doe): ")
    grade_level = input("What grade are you in (Grade 1-12): ")
    sub_topic_name = input("Enter the sub-topic you want to learn: ")

    # if student is in database, get the object
    if full_name in all_student_names:
        print(f"{full_name} is already in the database")
        student = StudentCollection.get_student(full_name)
    else:
        # if the student is not in the database, create the object
        print(f"{full_name} will be added to the database")
        student = students.Student(full_name,float(grade_level)) # initialize student


    mistakes = [] # initialize mistakes array for student
    # find out if the has data related to the subtopic
    if sub_topic_name in student.current_subtopic_names():
        sub_topic = student.get_subtopic(sub_topic_name)
    else:
        sub_topic = students.Subtopic(sub_topic_name,1)
        # connect subtopic object  to student object
        student.add_subtopic(sub_topic)
        sub_topic = student.get_subtopic(sub_topic_name)

        # find all student's old mistakes for subtopic
        mistakes = sub_topic.metrics.get_all_mistakes()
        # mistakes is a map with the following keys: communication, interpretation, computation, and conceptual

    # ask the student a question
    question = ask_question(student.name, sub_topic, user_type)

    # print(question)

    # receive answer,  calculate GPT answer, have a chance for the student to ask questions, evaluate student
    metric_updates = receive_respond_and_update(question, student, sub_topic, mistakes)

    # return metric_updates
    # # update the database
    #
    sub_topic.update_subtopic(metric_updates)

    # remove old object and add new object ( updates object if it already is in database)
    if student.name in all_student_names:
        StudentCollection.delete_student(student)

    StudentCollection.add_student(student)
    #
    # StudentCollection

    # Ask the student if they want to be asked another question.
    answer = input("Do you want another question? 'yes' or 'no' ")

    answer = answer.lower() # make the 'Yes' or 'No' lowercase

    while answer not in ("yes", "no"):
        answer = input("Invalid input; Please enter 'yes' or 'no': ")

    if answer == "yes":
        student_learning()
    else:
        print("Thank you for using GPT Tutor! Have a great day.")




# In[31]:


def main():
    """
    The main function that starts the learning process for either....
    The student, or GPT
    """
    # User: Uses GPT_Tutor to learn math
    # Trainer: Testing GPT_Tutors knowledge ( ~ to MemPrompt paper)

    valid = False # valid if you enter either 'user' or 'trainer'
    while not valid:
        usage_type = input("Type 'user' if you use GPT to learn. \nType 'trainer' if you want to train GPT_Tutor.\nType 'exit' to exit the program\n")

        usage_type = usage_type.lower() # makes sure letters are in lowercase

        if usage_type == "user":
            valid = True
            # Start the learning process.
            student_learning()

        if usage_type == "trainer":
            valid = True
            # Start GPT learning process
            mem_prompt_learning()
        if usage_type == "exit":
            valid = True
# In[32]:


# Check if the script is being run directly
if __name__ == "__main__":
    main()


# In[45]:


# grade_student_response("What is 99 * 99", "99 * 99 = 9801","Alice",20, "basic arithmetic", "the answer is 9801")


# In[437]:


# student_learning()


#%%
