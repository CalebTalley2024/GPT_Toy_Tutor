#!/usr/bin/env python
# coding: utf-8

# In[87]:


from dotenv import load_dotenv
import json
import openai
import numpy as np
import pandas as pd
import time


# In[88]:


# get syllabus
# df1 = pd.read_csv('topics.csv')
# df2 = pd.read_excel('GPT_tutor_topics(sub_topics_included).xlsx')
# df2


# In[89]:


# get key and model
openai.api_key = "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"
model_35 = "gpt-3.5-turbo"
student_data_path = "../data/students.json"


# In[90]:


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


# In[100]:


# temporary helper functions
def manual_level_reset(name, sub_topic, level):
    # Get data from students.json
    with open(student_data_path) as f:
        data = json.load(f)

    # Check if the student is in the database
    students = data['students']
    for student in students:
        if name in student:
            # Check if the student has a section for the given subtopic
            sections = student[name]
            for section in sections:
                if section['sub_topic'] == sub_topic:
                    # Reset the student's metrics
                    section['proficiency_metrics'] = clear_metrics(section['proficiency_metrics'])
                    section['level'] =  level
                    section['questions_answered'] = [0, 0, 0, 0, 0]
                    print(f"{name}'s data metrics for '{sub_topic}' has been reset.")
                    break

    print("level changed, database stats reset")
    # Write the updated data back to students.json
    with open(student_data_path, 'w') as f:
        json.dump(data, f, indent=4)


# In[75]:


def get_student_subtopic_level(student, sub_topic):
    # Read the JSON file
    file_path = student_data_path
    with open(file_path, "r") as file:
        database = json.load(file)

    # if we don't find the student, or the subtopic in the database, we will use the lowest level by default
    default_level = 1

    # Access the student's data from the database
    student_data = None
    for student_entry in database["students"]:
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
        print(f"student has not data for '{sub_topic}' in this database. They will be start at Level 1.")
        return default_level
    else:
        # Retrieve the level and proficiency scores
        level = sub_topic_data["level"]

    # Return the level and proficiency scores
    return level


# In[ ]:


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
def init_question(student, sub_topic):


    # Prompt for level choice
    #TODO integrate manually picking level
    print(" picking the level manually will only affect the type of questions you get")
    choice = input("Do you want to pick the level? (Y/N): ")

    # If statement based on the choice
    if choice.upper() == "Y":
        valid = True
        while valid:
                level = int(input("Enter the level: "))
                if level > 5 or level < 1:
                    print("Invalid level, pick again.")
                else:
                    valid = False
        # Reset student's level if needed
        manual_level_reset(student, sub_topic, level)
    else:
        level = get_student_subtopic_level(student, sub_topic)
    # criteria: tell GPT scales for proficiency and level

    init = f"Based on {student}'s database, the student's skill level for {sub_topic} is {level}. Please give {student} a test question based on {sub_topic} and follow up with a sentence like 'Explain how you got your answer'. Adjust the difficulty of the question based on his skill level and proficiency score. DO NOT include any other words. Do not put the answer in the prompt."
    criteria = f"Level is on a scale between 1 and 5, where 5 is the hardest level."

    # combine criteria and message
    message = f"{init} {criteria}"
    init_crit = {
        "role": "system",
        "content": message
    }

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


# In[92]:


# ask question to student
def ask_question(student, sub_topic):
    # make sure to only receive math answers and initialize the questions GPT will give
    filter_subject = filter_answers()
    filter_question = init_question(student, sub_topic)
    formatting, level_meaning = question_formatting()
    messages = [filter_subject, filter_question, formatting, level_meaning]
    # print(messages)
    tutor_question = get_response_text(messages)
    # here we print out the question GPT gives the student
    print(f"{tutor_question}: \n\n")
    return tutor_question


# In[93]:


# time: time it took the student to answer the question given from GPT
# returns
#   - the response the student gives
#   - the time it takes to get a response form the studnet
def get_student_timed_response():
    start_time = time.time()

    student_res = input() # response to question

    end_time =  time.time()
    end_time = end_time - start_time

    return student_res, end_time
def grade_student_response(question, student_answer, student,solve_time, sub_topic):
    # take in the student's answer, and the topic
    print("Answer: \n")
    question_message = {
        "role": "system",
        "content": f"You are a math tutor. The question that the user is answering is '{question}'."

    }
    answer_explained = {
        "role": "user",
        "content": f"{student}'s answer is {student_answer}. Tell whether the student got the question correct and give and provide an explanation of the correct answer. Also explain where the student is incorrect"
    }
    init_response_messages = [question_message,answer_explained]

    answer_res = get_response_text(init_response_messages)
    print(f"{answer_res}\n\n")

    print("Evaluation: \n")
    evaluation_messages = [
        {
            "role": "system",
            "content": f"The topic of the question is {sub_topic}. This is the question given to {student}: {question}. {student}'s answer is {student_answer}. This  is the answer you gave: {answer_res}."
        },
        {
            "role": "system",
            "content": f"This I need you to evaluate {student}'s performance in terms of the following skill metrics: communication, interpretation, computation, conceptual, and the time taken to solve the question (it took the student {solve_time} seconds to complete the question. For each of these metrics, rate the skill out of 5, where 5 out of 5 is the best score. make sure to have your evaluation in outline format. Also give an explanation on how {student} did not get the highest marks "
        },
        {
            "role": "system",
            "content": "at the end, give an average score based on the above metrics"
        }
    ]
    evaluation_res = get_response_text(evaluation_messages)
    print(evaluation_res)
    print(" \n\n")
    metrics_scores = extract_metrics_scores(evaluation_res)

    # print(metrics_scores)
    return  metrics_scores
def extract_metrics_scores(gpt_res):
    instruction = f"Extract the metric numbers:\n\n{gpt_res}\n\n---\n. Answer this question in the form of a JSON file"
    example_text = """
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
    example_res = """
        {
            "proficiency_metrics": {
                "proficiency_avg": 4.6,
                "communication": {
                    "score": 4,
                    "related_mistakes": ["could have been more elaboration and clarity in his explanation."]
                },
                "interpretation": {
                    "score": 5,
                    "related_mistakes": []
                },
                "computation": {
                    "score": 5,
                    "related_mistakes": []
                },
                "conceptual": {
                    "score": 4,
                    "related_mistakes": ["explanation could have included more conceptual details to further enhance his understanding"]
                },
                "time": {
                    "score": 5,
                    "seconds": 20
                }
            }
    }
    """
    messages=[
        {"role": "system", "content": instruction},
        {"role": "user", "content": example_text},
        {"role": "assistant", "content": example_res}]

    # get JSON data in form of response string
    metric_scores_string =  get_response_text(messages)

    # make the string a JSON

    metric_scores_json = eval(metric_scores_string)
    return metric_scores_json

    # # print(metric_scores_json)
    # return metric_scores_string


# In[79]:


# receive student cold ts answer, respond to their answer, and update their statistics
def _receive_respond_and_update(question, student, sub_topic):
    # Get the student's response and the time taken
    student_res, solve_time = get_student_timed_response()

    # Grade the student's response using the given question, student response, time, and sub_topic
    gpt_res = grade_student_response(question, student_res, student, solve_time, sub_topic)

    # Extract metric updates from the GPT response
    metric_updates = extract_metrics_scores(gpt_res)

    # Return the metric updates
    return metric_updates


# In[94]:


# helper functions for update_student_stats
def update_scores_and_average(database_scores, new_score):

    # the database stores the 3 most recent scores, so we will have to add our new_score and get rid of the old one

    # add new score
    # print(database_scores)
    database_scores += [new_score]
    # remove oldest score if there are more than 3 numbers in the list
    if len(database_scores) > 3:
        database_scores = database_scores[1:]

# get the avg score and round to the last 2 decimals
    new_avg_score = np.mean(database_scores)
    new_avg_score = round(new_avg_score, 2)
    return database_scores,new_avg_score
def is_level_update_needed(overall_avg_stats):
    bool = False
    avg_score, recent_scores =  overall_avg_stats["avg_score"],overall_avg_stats["recent_scores"]
    # if the avg score is 5, and we have 3 scores that make up the average, we need a level update
    if avg_score == 5 and len(recent_scores) == 3:
        bool = True
    return bool
def update_data(data,metrics_updates):

    metrics, level,questions_answered  =  data["proficiency_metrics"], data["level"],data["questions_answered"]

    # update metrics
    metrics = update_metrics(metrics,metrics_updates)
    # update level and questions_answered

    # each index of the array corresponds to the amount of questions answered a a certain level of difficulty
    questions_answered[level-1] += 1

    # if we have to upgrade to the next level, we get rid of our previous level's stats
    if is_level_update_needed(metrics["overall_avg"]):
        if level > 5:
            topic = data["topic"]
            print(f"Congratulations, you have mastered the topic: {topic} the highest level available. Please pick another topic to learn")
        else:
            level += 1
            print(f"Congratulations, you have moved up to Level {level}")
            metrics = clear_metrics(metrics) # remove previous level's data

    return metrics,level,questions_answered
def clear_metrics(old_metrics):
    metrics = {
        "overall_avg": {
            "avg_score": 0,
            "recent_scores": [
            ]
        },
        "communication": {
            "avg_score": 0,
            "related_mistakes": [
            ],
            "recent_scores": [
            ]
        },
        "interpretation": {
            "avg_score": 0,
            "related_mistakes": [],
            "recent_scores": []
        },
        "computation": {
            "avg_score": 5.0,
            "related_mistakes": [],
            "recent_scores": []
        },
        "conceptual": {
            "avg_score": 0,
            "related_mistakes": [],
            "recent_scores": []
        },
        "time": {
            "avg_score": 0,
            "avg_times": None,
            "recent_times": [
            ],
            "recent_scores": [
            ]
        }}
    return metrics
def update_metrics(metrics, metric_updates):

    metric_types = ['overall_avg', 'communication', 'interpretation', 'computation', 'conceptual', 'time']

    for metric_type in metric_types:
        metric, metric_update = metrics[metric_type], metric_updates[metric_type]

        if metric_type == 'overall_avg':
            new_score = metric_update
        else:
            new_score = metric_update['score']
            if 'related_mistakes' in metric_update:
                metric['related_mistakes'] = metric_update['related_mistakes']
            if 'seconds' in metric_update:
                new_time = metric_update['seconds']
                metric['recent_times'], metric['avg_times'] = update_scores_and_average(metric['recent_times'], new_time)

        metric['recent_scores'], metric['avg_score'] = update_scores_and_average(metric['recent_scores'], new_score)

    return metrics

# updates the student metrics in the database
def update_student_stats(name, sub_topic, metric_updates):
    # Get data from students.json
    with open(student_data_path) as f:
        data = json.load(f)

    # Check if the student is in the database
    students = data["students"]
    for student in students:
        if name in student:
            # Check if the student has a section for the given subtopic
            sections = student[name]
            for section in sections:
                if section["sub_topic"] == sub_topic:
                    # Update the student's metrics
                    section["proficiency_metrics"], section["level"],section["questions_answered"], = update_data(section,metric_updates)
                    print(f"{name}'s data metrics for '{sub_topic}'has been updated ")
                    break
            else:
                # If the student does not have data for that subtopic, add metric_updates
                sections.append({
                    "sub_topic": sub_topic,
                    "level": 1,
                    "questions_answered": [1,0,0,0,0],
                    "proficiency_metrics": metric_updates
                })
                print(f"{name}'s data metrics for '{sub_topic}'has been added ")

            break
    else:
        # If the student is not found in the database, create a new entry
        students.append({
            name: [{
                "sub_topic": sub_topic,
                "level": 1,
                "questions_answered": [1,0,0,0,0],
                "proficiency_metrics": metric_updates
            }]
        })
        print(f"{name}'s data metrics for '{sub_topic}'has been added ")
    # Write the updated data back to students.json
    with open(student_data_path, 'w') as f:
        json.dump(data, f, indent=4)

# asks student question, evaluates and updates their database
def student_learning(student, sub_topic):
    """Asks the student a question and updates their stats."""
    question = ask_question(student, sub_topic)
    metric_updates = _receive_respond_and_update(question, student, sub_topic)
    update_student_stats(student, sub_topic, metric_updates)

    # Ask the student if they want to be asked another question.
    answer = input("Do you want another question? 'Yes' or 'No' ")
    while answer not in ("Yes", "No"):
        answer = input("Please enter 'Yes' or 'No': ")

    if answer == "Yes":
        student_learning(student, sub_topic)
    else:
        print("Thank you for using the learning assistant! Have a great day.")
# In[83]:


#TODO make a test portion


# In[ ]:


def main():
    """The main function that starts the learning process."""
    student = input("Enter your name: ")
    sub_topic = input("Enter the sub-topic you want to learn: ")

    # Start the learning process.
    student_learning(student, sub_topic)

# In[109]:


# Check if the script is being run directly
if __name__ == "__main__":
    main()


# In[ ]:


# Example metric updates
# updated_metrics = {
#     "overall_avg": 4,
#     "communication": {
#         "score": 4,
#         "related_mistakes": ["needs to provide more examples"]
#     },
#     "interpretation": {
#         "score": 5,
#         "related_mistakes": []
#     },
#     "computation": {
#         "score": 5,
#         "related_mistakes": []
#     },
#     "conceptual": {
#         "score": 4,
#         "related_mistakes":  ["forgot to add 1", "forgot to simplify"]
#     },
#     "time": {
#         "score": 2,
#         "seconds": 300
#     }
# }
# updated_metrics_2 = {
#     "overall_avg": 5,
#     "communication": {
#         "score": 5,
#         "related_mistakes": []
#     },
#     "interpretation": {
#         "score": 5,
#         "related_mistakes": []
#     },
#     "computation": {
#         "score": 5,
#         "related_mistakes": []
#     },
#     "conceptual": {
#         "score": 5,
#         "related_mistakes":  []
#     },
#     "time": {
#         "score": 5,
#         "seconds": 30
#     }
# }

