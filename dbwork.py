from pymongo import MongoClient
client = MongoClient(
    'mongodb+srv://test:test@cluster0.hknxc.mongodb.net/myFirstDatabase?retryWrites=true&w=majority')

db = client['userdb']
col = db['users']


def insert(username, password):
    a = list(col.find({"username": username}))
    if len(a) == 1:
        return False
    else:
        col.insert_one({"username": username, "password": password})
        return True


def find(username, password):
    print("Username:", username, "\nPassword:", password)
    a = col.find_one({"username": username})
    print("Printing what is a:", a)
    return a
