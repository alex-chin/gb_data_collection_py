import pymongo
import datetime as dt

# client = pymongo.MongoClient("mongodb://127.0.0.1:2701/database")
client = pymongo.MongoClient()
database = client['some_database']
collection = database['first_database']

data = {
    "some": dt.datetime.now(),
    "True": 2,
    "1": "Hello",
    "2": [1, 2, 2, 3, 4],
    "3": {"1": 1, "2": 2, "3": 3}
}

collection.insert_one(data)

print(1)
