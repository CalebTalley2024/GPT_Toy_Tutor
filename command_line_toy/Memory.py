import Toy_Test as TT
from sklearn.metrics.pairwise import cosine_similarity as cos
from sentence_transformers import SentenceTransformer as ST
import numpy as np
import re
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi

# password for MongoDB
password = "GPTTutor"

# connect to MongoDB database
uri = f"mongodb+srv://CalebTalley:{password}@cluster0.b3k8luy.mongodb.net/?retryWrites=true&w=majority"
# Create a new client and connect to the server
client = MongoClient(uri, server_api=ServerApi('1'))

# Send a ping to confirm a successful connection
try:
    client.admin.command('ping')
    print("Pinged your deployment. You successfully connected to MongoDB!")
except Exception as e:
    print(e)


# collection: data called from MongoDB
# json: data in json
class Memories:
    def __init__(self):
        self.collection = client["Memory"]["Memory0"]
        self.json = list(client["Memory"]["Memory0"].find())

    def get_memory(self, question):
        # returns memory that fits the question
        return list(self.collection.find({"Question": question}))[0]

    def get_questions(self):
        return [question["Question"] for question in self.json]

    # single memorys
    def get_feedback_at_index(self,i):
        return list(self.collection.find().skip(i).limit(1))[0]

    # update feedback for single memory
    # add memory if it is not already in the database
    def update_memory_feedback(self,question , feedback):
        if self.collection.count_documents({"Question": question}) > 0:
            memory = self.get_single_memory(question)
            memory["Feedback"].append(feedback)
        else:
            new_memory = {
                "Question": question,
                "Feedback": [feedback],
            }
            self.collection.insert_one(new_memory)
            print("the question and the feedback has been added to memory")

# Generate sentence embeddings for all the keys in the JSON file.
# does cosine similarity for Questions ONLY
# returns most similar memory and  feedback
# if the question is already in the database, it will still be returned with this function ( similarity will equal 1)
def find_most_similar_memory(query):
    # get Memory in both collection and JSON format
    memories0 = Memories()
    model = ST('all-MiniLM-L6-v2')

    # Load the JSON file.
    memory_json = memories0.json

    # Preprocess the query to all lowercase.
    query = query.lower()

    # embed the query
    query_embed = model.encode(query)

    print(query)

    # Get all of the questions that are in the database
    questions = memories0.get_questions()

    # embed the memory's questions into vector representation
    memory_embeds = model.encode(questions)

    # calculate the cosine similarity of each embed from memory compared to the query embed
    cos_sim = cos([query_embed], memory_embeds)

    # get the index of the question with the highest similarity score
    most_similar_question_index = int(np.argmax(cos_sim))

    most_similar_question = memories0.get_feedback_at_index(most_similar_question_index)["Question"]
    most_similar_feedback = memories0.get_feedback_at_index(most_similar_question_index)["Feedback"]

    return most_similar_question, most_similar_feedback





