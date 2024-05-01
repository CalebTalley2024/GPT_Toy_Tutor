#!/usr/bin/env python
# coding: utf-8

# In[5]:


import json
import numpy as np
from database_connect import client # gets MongoDB client, which gives access to data


# In[6]:
# collection: data called from MongoDB
# json: data in json
def print_line(len = 150):
    print("-" * len)


# constants
# default collection used
main_collection = "Section0"


# In[7]:


# examples for visualizing jsons
# format of 'all_updates':


# In[80]:


# recursively create JSON
def obj_to_dict(obj):
    # recursive calls run depending on if the call's obj is a list, dictionary, object, or primitive ( int, string, float, etc)
    if isinstance(obj, list): # if list
        return [obj_to_dict(e) for e in obj]
    elif isinstance(obj, dict): # if dictionary or object
        return {str(key): obj_to_dict(value) for key, value in obj.items()}
    elif hasattr(obj, '__dict__'): # if object
        return {str(key): obj_to_dict(value) for key, value in obj.__dict__.items()}
    else: # if primitive
        return obj

# converts dictionary into student object
def dict_to_student(dict_data):
    # print(dict_data)
    # Initialize student Object
    student = Student(dict_data['name'])
    # Initialize and fill subtopics
    for subtopic_data in dict_data['subtopics']:
        subtopic = Subtopic(subtopic_data['name'], subtopic_data["grade"], subtopic_data["education_lvl"],subtopic_data["topic_name"])  # create Subtopic Object

        # Fill in metrics data
        metrics_map_data = subtopic_data['metrics_map']
        for level, metrics_data in metrics_map_data.items(): # level is the key to the hashmap
            metrics_obj = Metrics()  # Create Metrics object for this level
            # print(metrics_data.keys())

            # make metric object references
            overall_avg_obj = metrics_obj.overall_avg
            communication_obj = metrics_obj.communication
            interpretation_obj = metrics_obj.interpretation
            computation_obj = metrics_obj.computation
            conceptual_obj = metrics_obj.conceptual
            time_obj = metrics_obj.time

            # update all metric objects
            for metric in [ overall_avg_obj, communication_obj,interpretation_obj,computation_obj, conceptual_obj, time_obj]:
                metric_type = metric.metric_type # eg. communication
                metric_json = metrics_data[metric_type]
                metric.avg_score = metric_json["avg_score"]
                metric.previous_scores = metric_json["previous_scores"]
                metric.num_questions = metric_json["num_questions"]
                if metric_type == "time":
                    metric.avg_time = metric_json["avg_time"]
                    metric.recent_times = metric_json["recent_times"]
            # metrics_obj.update(metrics_info)  # Update metrics
            subtopic.metrics_map[level] = metrics_obj

        student.add_subtopic(subtopic)
    student.mistakes = dict_data["mistakes"]

    return student  # Return the completed student object

# In[28]:


class StudentsCollection:
    def __init__(self, collection = "Section0"):
        database = client["Students"]
        self.name = collection
        self.collection = database[collection] # a collection ( ex: Section0)
    def add_student(self,student):
        # make student into dictionary format
        student_dict = student.in_dict_format()
        self.collection.insert_one(student_dict)
        print(f"{student.name} has been added to collection: {self.name}")
    # takes in student's name
    # returns wanted student from database or None (student is not in database)
    def get_student(self, student_name):
        query = {"name": student_name}
        # Fetch the student data as a list
        student_dict_list = list(self.collection.find(query))
        try:
            if not student_dict_list:  # Checks if the list is empty
                raise ValueError("No student found with the given name.")
            # Get the first student_dict from the list (assuming there should only be one)
            student_dict = student_dict_list[0]
            # Do something with student_dict
            student_obj = dict_to_student(student_dict)
            print("Student found:", student_obj.name)
            return student_obj

        except ValueError as e:
            print(e)
    def delete_student(self,student):
        query = {"name": student.name}
        self.collection.delete_one(query)
        print(f"{student.name} has been deleted from collection: {self.name}")
    # gets list of all students in collection
    def current_student_names(self):
        student_names = []
        student_data = list(self.collection.find())

        for datam in student_data:
            student_names.append(datam["name"])
        return student_names

class Student:
    def __init__(self,name):
        self.name = name
        # self.grade = grade
        self.subtopics = [] # array of Subtopic objects
        self.mistakes = np.empty((0, 2)) # init as 0 x 2 array (Question, Mistakes) #TODO later add is_student_answer_correct

    def in_dict_format(self):
        return obj_to_dict(self)

    def current_subtopic_ids(self):
        if not len(self.subtopics) == 0:
            return list(map(lambda subtopic: subtopic.id, self.subtopics))
        else:
            return []

    # gets the subtopic
    def get_subtopic(self, subtopic_id):
        for i, id in enumerate(self.current_subtopic_ids()):
            if id == subtopic_id:
                print(f"The subtopic is already in {self.name}'s database")
                return self.subtopics[i]
        # if name not found
        print(f"{subtopic_id} not found in database, so it will be created")
        # subtopic = Subtopic(subtopic_name,1)
        # return subtopic
    def add_subtopic(self,subtopic):
        return self.subtopics.append(subtopic)

    # adds array (question, mistake) to student's data
    def add_mistakes(self, all_updates):
        question = all_updates["question"]
        mistakes = all_updates["mistakes"]
        # Assuming mistakes is a list, add them individually
        # print(f"question: {question}\n\n mistakes: {mistakes}")
        # for mistake in mistakes:
        row = np.array([question, mistakes])  # Shape: (2, )
        self.mistakes = np.vstack((self.mistakes, row))  # Add within a list to preserve shape
        self.mistakes = self.mistakes.tolist() # np --> list

    def to_json(self):
        # create json with everything
        student_json = {
            "name": self.name,
            # "grade": self.grade,
            # convert subtopics to jsons before putting them into student.json
            "subtopics": list(map(lambda subtopic: subtopic.to_json(), self.subtopics)),
            "mistakes": self.mistakes
        }
        return student_json


# In[29]:


# SC = StudentsCollection()
# Alice = SC.get_student("Alice Carter")
# Alice.current_subtopic_names()


# In[29]:





# In[30]:


class Subtopic:
    def __init__(self, name, grade, education, topic_name):
        # how many questions you answered for each of the 5 levels of a topic
        self.name = name # subtopic name
        self.grade = grade
        self.education_lvl = education
        self.topic_name = topic_name # the subtopic is a subset of the overall topic
        self.id = f"{grade}|{education}|{topic_name}|{name}"
        self.metrics_map = {} # Hashmap of metrics (key: level, value: Metrics Object)
    # all_updates: string or json or dictionary: updates that need to be done for metrics
    def update_subtopic(self, all_updates):
        # update the metrics
        # find hashmap value/metrics object that corresponds to the level/key
        print_line(1000)
        key = all_updates["level"]
        if not self.metrics_map.get(key, None): # if None,
            # add default Metrics object if isn't one in the map at the key
            self.metrics_map[key] = Metrics()
        metrics_to_update = self.metrics_map[key]
        print_line(1000)
        metrics_to_update.update(all_updates)
    # returns and prints subtopic data in a json
    def to_json(self):
        subtopic_json = {
            "name": self.name,
            "grade": self.grade,  # Include grade
            "education_lvl": self.education_lvl,  # Include education level
            "topic_name": self.topic_name,  # Include topic name
            "metrics_map": {}
        }
        # add all related metrics by level
        for level, metrics in self.metrics_map.items():
            subtopic_json["metrics_map"][level] = metrics.to_json()

        subtopic_json = json.dumps(subtopic_json, indent=2)
        # print(subtopic_json)
        return subtopic_json  # Return the JSON string with indentation


# In[61]:


class Metrics:
    def __init__(self):
        self.overall_avg = Metric("overall_avg")
        self.communication = Metric("communication")
        self.interpretation = Metric("interpretation")
        self.computation = Metric("computation")
        self.conceptual = Metric("conceptual")
        self.time = Metric("time")

    # returns dictionary of mistakes
    # key = metric type, value: the actual mistakes
    def get_all_mistakes(self):
        mistakes = {}
        mistakes["communication"] = self.communication.related_mistakes
        mistakes["interpretation"] = self.interpretation.related_mistakes
        mistakes["computation"] = self.computation.related_mistakes
        mistakes["conceptual"] = self.conceptual.related_mistakes
        return mistakes # convert dict to string

    # update metric given update metrics in json/dict
    def update(self, all_updates):
        # attributes each metric has
        # if the json does not have a value for an update, the value in the Metric object will remain unchanged
        avg_comm = self.communication.update(all_updates["communication"])
        avg_interp = self.interpretation.update(all_updates["interpretation"])
        avg_comp = self.computation.update(all_updates["computation"])
        avg_conc = self.conceptual.update(all_updates["conceptual"])
        avg_time = self.time.update(all_updates["time"])
        # update overall_avg
        # get average score of the newly calculated metrics
        new_average = np.mean([avg_comm,avg_interp,avg_comp,avg_conc,avg_time])
        # print(f"\n calculating overall avg")

        prev_scores = self.overall_avg.previous_scores
        prev_scores.append(new_average)
        if len(prev_scores) == 6:
            prev_scores.pop(0)
        # us the average of average scores to get the new "overall avg" score
        self.overall_avg.avg_score = np.mean(prev_scores)
    def to_json(self):
        metrics_json = {
            "overall_avg": self.overall_avg.to_json(),
            "communication": self.communication.to_json(),
            "interpretation": self.interpretation.to_json(),
            "computation": self.computation.to_json(),
            "conceptual": self.conceptual.to_json(),
            "time": self.time.to_json()
        }
        return metrics_json


# In[65]:


class Metric:
    # special types: time, overall_avg
    # order of recent_times and related mistakes (oldest..... newest)
    def __init__(self, metric_type = None):
        self.metric_type = metric_type
        self.avg_score = 0
        self.previous_scores = []
        self.num_questions = 0      # total number of questions asked
        if metric_type == "time":
            self.avg_time = None
            self.recent_times = []

    # updates metrics given json of new data
    # NOT USED to update overall_avg ( can only be updated in "Metrics" object
    # update: JSON
    # returns average score for metric
    #TODO figure out `TypeError: 'int' object is not subscriptable` error
    def update(self, update):
        # update num_questions
        self.num_questions += 1
        # get metrics previous scores and add new score,
        prev_scores = self.previous_scores

        # prev_scores.append(update["score"])
        # attempt to add the update to the previous score
        try:
            prev_scores.append(update["score"]) # appending the score
        except (KeyError, TypeError) as e:
            # Handle the potential errors
            print(f"Error appending score: {e}\n")
            print("--------------------------------------------------------")
            print(update)
            print("--------------------------------------------------------")
            return -1

        # remove oldest score
        if len(prev_scores) == 6:
            prev_scores.pop(0)
        # get the average
        self.avg_score = np.mean(prev_scores)

        # if there is  time attribute, update the time data:
        if hasattr(self, 'recent_times'):
            recent_times = self.recent_times
            recent_times.append(update["seconds"])
            if len(recent_times) == 6:
                recent_times.pop(0)
            self.avg_time = np.mean(recent_times)
            # print("time average",self.avg_time)
            # print("recent times",self.recent_times)
        return self.avg_score

    def to_json(self):
        metric_json = {
            "avg_score": self.avg_score,
            "previous_scores": self.previous_scores,
            "num_questions": self.num_questions
        }
        if hasattr(self, "avg_time"):
            metric_json["avg_time"] = self.avg_time
            metric_json["recent_times"] = self.recent_times
        # if not hasattr(self,"overall_avg"):
        #     metric_json["previous_scores"]: self.previous_scores
        # elif hasattr(self, "related_mistakes"):
        #     metric_json["related_mistakes"] = self.related_mistakes

        return metric_json

#%%
