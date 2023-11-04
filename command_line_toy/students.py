import numpy as np
from database_connect import client # gets MongoDB client, which gives access to data

# constants
# default collection used
main_collection = "Section0"

# recursively create JSON
def obj_to_dict(obj):
    # recursive calls run depending on if the call's obj is a list, dictionary, object, or primitive ( int, string, float, etc)
    if isinstance(obj, list): # if list
        return [obj_to_dict(e) for e in obj]
    elif isinstance(obj, dict): # if dictionary or object
        return {key: obj_to_dict(value) for key, value in obj.items()}
    elif hasattr(obj, '__dict__'): # if object
        return {key: obj_to_dict(value) for key, value in obj.__dict__.items()}
    else: # if primitive
        return obj

# converts dictionary into student object
def dict_to_student(dict_data):
    # Initialize student Object
    student = Student(dict_data['name'], dict_data['grade'])

    # Initialize and fill subtopics
    for subtopic_data in dict_data['subtopics']:
        subtopic = Subtopic(subtopic_data['subtopic_name'], subtopic_data['grade'])
        subtopic.num_questions_answered = subtopic_data['num_questions_answered']

        metrics_data = subtopic_data['metrics']
        metrics = Metrics()

        for metric_name, metric_data in metrics_data.items():
            metric = Metric()
            metric.avg_score = metric_data['avg_score']
            metric.previous_scores = metric_data['previous_scores']

            if 'avg_time' in metric_data:
                metric.avg_time = metric_data['avg_time']
            if 'recent_times' in metric_data:
                metric.recent_times = metric_data['recent_times']
            if 'related_mistakes' in metric_data:
                metric.related_mistakes = metric_data['related_mistakes']

            setattr(metrics, metric_name, metric)

        subtopic.metrics = metrics
        student.subtopics.append(subtopic)

    return student

class StudentsCollection:
    def __init__(self, collection):
        database = client["Students"]
        self.name = collection
        self.collection = database[collection] # a collection ( ex: Section0)

    def add_student(self,student):
        # make student into dictionary format
        student_dict = student.in_dict_format()
        self.collection.insert_one(student_dict)
        print(f"{student.name} has been added to collection: {self.name}")

    # takes in student's name
    # returns wanted student from database
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
    def __init__(self,name, grade: float):
        self.name = name
        self.grade = grade
        self.subtopics = [] # array of Subtopic objects

    def in_dict_format(self):
        return obj_to_dict(self)


class Subtopic:
    def __init__(self, subtopic_name, level):
        # how many questions you answered for each of the 5 levels of a topic
        self.subtopic_name = subtopic_name
        self.level = level # range: 1 - 5
        self.num_questions_answered = [0,0,0,0,0] # on slot per level (5 total levels)
        # self.num_questions_answered = [5,5,5,5,5]
        self.metrics = Metrics()

    # resets metrics
    def clear_metrics(self):
        self.metrics = Metrics()

    # TODO need to be tested
    # updates the level if the metrics have a perfect score for the last 5 questions
    def update_level(self):
        #check teh amount of questions answered for the current level
        ques_answered = self.num_questions_answered
        num_questions_current_level = ques_answered[self.level-1] # -1 b/c of 0 based indexing
        # if a student has been asked 5 questions, AND the average score for the metrics is 5...... increment the level
        average_score_current_level = self.metrics.overall_avg.avg_score
        # print(num_questions_current_level )
        if num_questions_current_level == 5 and average_score_current_level == 5:
            self.level += 1
            print(f"Subtopic '{self.subtopic_name}' has been upgraded to level {self.level}")
        else:
            print("level has not been updated")

    # metric_updates: string or json or dictionary: updates that need to be done for metrics
    def update_subtopic(self, all_updates):
        # find level
        # print("current level ", self.level)
        level = self.level
        # update the metrics
        self.metrics.update(all_updates)
        # update the amount of quesitons
        # add 1 to the index that corresponds to the level ( "index -1" because the array is 0 based)
        self.num_questions_answered[level-1] +=1
        # update the level if needed
        self.update_level()

    # returns and prints subtopic data in a json
    def to_json(self):
        subtopic_json = {
            "subtopic_name": self.subtopic_name,
            "level": self.level,
            "num_questions_answered": self.num_questions_answered,
            "metrics": self.metrics.to_json()  # Convert metrics to JSON
        }

        # subtopic_json = json.dumps(subtopic_json, indent=1)
        print(subtopic_json)
        return subtopic_json  # Return the JSON string with indentation



class Metrics:

    def __init__(self):
        self.overall_avg = Metric("overall_avg")
        self.communication = Metric()
        self.interpretation = Metric()
        self.computation = Metric()
        self.conceptual = Metric()
        self.time = Metric("time")

    # returns dictionary of mistakes
    # key = metric type, value: the actual mistakes
    def get_all_mistakes(self):
        mistakes = {}
        print("function starts")
        mistakes["communication"] = self.communication.related_mistakes
        mistakes["interpretation"] = self.interpretation.related_mistakes
        mistakes["computation"] = self.computation.related_mistakes
        mistakes["conceptual"] = self.conceptual.related_mistakes
        return str(mistakes) # convert dict to string

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

        # print("score avg", self.overall_avg.avg_score)
        # print("previous scores",self.overall_avg.previous_scores)
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


class Metric:
    # special types: time, overall_avg

    # order of recent_times and related mistakes (oldest..... newest)
    def __init__(self, metric_type = None):
        self.avg_score = 0
        self.previous_scores = []
        if metric_type == "time":
            self.avg_time = None
            self.recent_times = []
        elif metric_type != "overall_avg" and metric_type == "time" :
            self.related_mistakes = []

    # updates metrics given json of new data
    # NOT USED to update overall_avg ( can only be updated in "Metrics" object
    # update: JSON
    # returns average score for metric
    def update(self, update):
        # get metrics previous scores
        prev_scores = self.previous_scores
        # add new score,
        prev_scores.append(update["score"])
        # remove oldest score
        if len(prev_scores) == 6:
            prev_scores.pop(0)
        # get the average
        self.avg_score = np.mean(prev_scores)
        # print("score avg", self.avg_score)
        # print("previous scores",self.previous_scores)

        # replace related mistakes
        if hasattr(self, 'related_mistakes'):
            self.related_mistakes = update["related_mistakes"]
            # print("related mistakes",self.related_mistakes)

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
            "previous_scores": self.previous_scores
        }
        if hasattr(self, "avg_time"):
            metric_json["avg_time"] = self.avg_time
            metric_json["recent_times"] = self.recent_times
        elif hasattr(self, "related_mistakes"):
            metric_json["related_mistakes"] = self.related_mistakes

        return metric_json
