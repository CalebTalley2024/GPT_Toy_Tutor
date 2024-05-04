from dotenv import load_dotenv
import os
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi

load_dotenv()
password = os.getenv('MONGODB_PASSWORD_1')

uri = f"mongodb+srv://CalebTalley:{password}@cluster0.b3k8luy.mongodb.net/?retryWrites=true&w=majority" #TODO Add environment variables later
# Create a new client and connect to the server
client = MongoClient(uri, server_api=ServerApi('1'))

# Send a ping to confirm a successful connection
try:
    client.admin.command('ping')
    print("Pinged your deployment. You successfully connected to MongoDB!")
except Exception as e:
    print(e)