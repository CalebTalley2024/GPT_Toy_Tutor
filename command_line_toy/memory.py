#!/usr/bin/env python
# coding: utf-8

# In[3]:


from sklearn.metrics.pairwise import cosine_similarity as cos
from sentence_transformers import SentenceTransformer as ST
import numpy as np
from database_connect import client # gets MongoDB client, which gives access to data
# from learning import print_line

# In[4]:
def print_line(len = 150):
    print("-" * len)


# collection: data called from MongoDB
# json: data in json
class MemPrompt:
    def __init__(self):
        # self.collection = client["Memory"]["Memory0"]
        # different memprompt databases
        self.questions = Memory_Collection("Q")
        self.answers = Memory_Collection("A")
        self.evaluations = Memory_Collection("E")

class Memory_Collection:
    # creates collection object
    # properties:  collection, type, json
    def __init__(self, mem_type):
        """
        mem types: char
        'A': answer
        'Q': question
        'E': evaluation
        """
        if mem_type == 'Q': # query = question
            self.collection = client["MemPrompt"]["Questions"]
            self.type = "Questions"
        elif mem_type == 'A': # query = question
            self.collection = client["MemPrompt"]["Answers"]
            self.type = "Answers"
        elif mem_type == 'E': # query = (GPT answer + student answer) pair
            self.collection = client["MemPrompt"]["Evaluations"]
            self.type = "Evaluations"
        else:
            ValueError("Invalid mem_type: should be 'A', 'Q', or 'E'")

        self.json = list(self.collection.find()) # interpretable json of the data

    # the query is one of the following .....
    # question
    # (GPT answer + student answer) pair
    def get_memory_row(self, query):
        # returns memory that fits the question
        memory = list(self.collection.find({"Query": query}))
        if not memory:
            raise ValueError(f"No memory for query: {query}")
        # print(memory[0])
        return memory[0]

    # update feedback for single memory
    # add memory if it is not already in the database
    # updates/adds memory row to collection on MongoDB
    def update_memory_feedback(self, query, feedback):
        if self.collection.count_documents({"query": query}) > 0:
            # get existing row
            memory = self.get_memory_row(query)
            # delete the old row
            self.collection.delete_one({"Query":query})
            # make new memory row
            feedback_list = memory["Feedback"] # feedback list ---> string
            feedback_list.append(feedback)

            new_memory = {
                "Query": memory["Query"],
                "Feedback": feedback_list
            }
            self.collection.insert_one(new_memory) # update datebase on MongoDB
            print("the query and the feedback has been updated to memory")
        else:
            new_memory = {
                "Query": query,
                "Feedback": [feedback],
            }
            self.collection.insert_one(new_memory) #update database on MongoDB

            # reinitialilze the object collection (allows MongoDB to update the 'self' object
            # update the correct database

            if self.type == "Questions": # query = question
                self.collection = client["MemPrompt"]["Questions"]
            elif self.type == "Answers": # query = question
                self.collection = client["MemPrompt"]["Answers"]
            elif self.type == "Evaluations": # query = (GPT answer + student answer) pair
                self.collection = client["MemPrompt"]["Evaluations"]

            print("the query and the feedback has been added to memory")

            # update the json
            self.json = list(self.collection.find())

        return 0

    # get the queries for the memory collection
    def get_queries(self):
        return [query["Query"] for query in self.json]

        # get single memory by index
    def get_row_at_index(self,i):
        return list(self.collection.find().skip(i).limit(1))[0]

    # Generate sentence embeddings for all the keys in the JSON file.
    # does cosine similarity for Questions ONLY
    # returns most similar memory and  feedback
    # if the question is already in the database, it will still be returned with this function ( similarity will equal 1)
    def find_most_similar_memory(self, query):
        # get Memory in both collection and JSON format
        model = ST('all-MiniLM-L6-v2')
        # Load the JSON file.
        # memory_json = memories0.json
        # Preprocess the query to all lowercase.
        query = query.lower()
        # embed the query
        query_embed = model.encode(query)
        # print(query)
        # Get all of the queries that are in the database
        queries = self.get_queries()
        if queries == []: # if there are no queries
            return " ", [] # return empty string for query and empty array for response
        
        # embed the memory's questions into vector representation
        memory_embeds = model.encode(queries)
        # calculate the cosine similarity of each embed from memory compared to the query embed
        cos_sim = cos([query_embed], memory_embeds)
        # get the index of the question with the highest similarity score
        most_similar_query_index = int(np.argmax(cos_sim))

        most_similar_row = self.get_row_at_index(most_similar_query_index)
        if most_similar_row:
            most_similar_query, most_similar_feedback = most_similar_row["Query"], most_similar_row["Feedback"]
        else:
            print("There is no feedback")
            return "", ""

        return most_similar_query, most_similar_feedback

    # return feedback associated with query, if you get an error, return empty string
    # def get_feedback_w_query(self,query):
    #     try:
    #         row = self.get_memory_row(query)
    #         if row:
    #             return row["Feedback"]
    #         else:
    #             print(f"no row for {query}")
    #             return ""
    #
    #     except ValueError:
    #         return ""
    #

    # will update the memory if the user spots a mistake that GPT has made in the answer and/or the explanation of the answer

    # info_1 and info_2 are different for different memory types
    # if question:
    #     - info_1 = grade|education|topic_name|subtopic_name
    #     - info_2 = None
    #     - info_3 = None
    #     - info_4 = None
    # if Answers:
    #     - info_1 = Answer
    #     - info_2 = Explanation
    #     - info_3 = None
    #     - info_4 = None
    # if Evaluation:
    #     - info_1 = GPT Answer
    #     - info_2 = Student Answer
    #     - info_3 = Evaluation result

    # returns whether or not feedback was needed
    def give_feedback(self, question, info_1, info_2 = None, info_3 = None): # TODO Test
        print_line()
        print_line()
        if self.type == "Questions": # query = question
            print(f"Subtopic Info: Grade {info_1}")
            print(f"Proposed Question: {question}\n")
        elif self.type == "Answers": # query = question
            # print(f"Question: {question}\n")
            # print(f"Proposed Answer: \n{info_1}\n")
            print(f"Proposed Answer + Explanation: \n{info_2}\n")
        elif self.type == "Evaluations": # query = (GPT answer + student answer) pair
            print(f"Question: {question}\n")
            print(f"Answer: {info_1}\n")
            print(f"Answer Response: {info_2}\n")
            # print(f"Time: {info_3} seconds \n")
            print(f"Proposed Evaluation: {info_3}\n")
        print_line()
        print_line()
        # first display the answer to the user
        need_feedback = input(f"{self.type[:-1]}: above require any feedback: 'Y' for yes, 'N' for no: ") # self.type[:-1]: plural -> singular
        if need_feedback.lower() == 'y':
            feedback = input("What needs to be improved in the analysis process?: ")
            if self.type == "Questions": # query = subtopic info
                self.update_memory_feedback(info_1, feedback)
            elif self.type == "Answers":
                self.update_memory_feedback(question, feedback)
            elif self.type == "Evaluations":
                self.update_memory_feedback(info_2, feedback) # query = GPT's Answer Response
            return True
        else:
            print("memory will not be updated")
            return False

