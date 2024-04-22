#!/usr/bin/env python
# coding: utf-8

# In[296]:


from sklearn.metrics.pairwise import cosine_similarity as cos
from sentence_transformers import SentenceTransformer as ST
import numpy as np
from database_connect import client # gets MongoDB client, which gives access to data


# In[297]:


# collection: data called from MongoDB
# json: data in json
class MemPrompt:
    def __init__(self):
        # self.collection = client["Memory"]["Memory0"]
        # different memprompt databases
        self.answers = Memory_Collection("A")
        self.evaluation = Memory_Collection("Q")
        self.questions = Memory_Collection("E")
        # self.json = list(client["Memory"]["Memory0"].find())
        
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
            self.collection = client["MemPrompt"]["Evaluation"]
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
                self.collection = client["MemPrompt"]["Evaluation"]

            print("the query and the feedback has been added to memory")

            # update the json
            self.json = list(self.collection.find())

        return 0

    # get the queries for the memory collection
    def get_queries(self):
        return [query["Query"] for query in self.json]
    
        # get single memory by index
    def get_feedback_at_index(self,i):
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
        print(query)
    
        # Get all of the questions that are in the database
        questions = self.get_queries()
        # embed the memory's questions into vector representation
        memory_embeds = model.encode(questions)
        # calculate the cosine similarity of each embed from memory compared to the query embed
        cos_sim = cos([query_embed], memory_embeds)
        # get the index of the question with the highest similarity score
        most_similar_query_index = int(np.argmax(cos_sim))
    
        most_similar_query = self.get_feedback_at_index(most_similar_query_index)["Query"]
        most_similar_feedback = self.get_feedback_at_index(most_similar_query_index)["Feedback"]
    
        return most_similar_query, most_similar_feedback



# In[299]:


# mem = MemPrompt()
# a = mem.answers
# a.find_most_similar_memory("What is 1 + 1")

# a.update_memory_feedback("What is 1 + 1", " do not append the numbers")
# a.get_queries()
# a.json


# In[ ]:




