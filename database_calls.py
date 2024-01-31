import pymongo

my_client = pymongo.MongoClient("mongodb://localhost:27017/")
my_database = my_client["ProjectTwo"]
my_collection_one = my_database["CollectionOne"]
my_collection_two = my_database["CollectionTwo"]

# 1. List of all work done by user TDanza.

query = {"Name of user on file": "TDanza"}
result = my_collection_two.find(query)

work_done_by_TDanza = []

for doc in result:
    work_done_by_TDanza.extend(doc["Location/Frames to fix"])
print("Work done by TDanza:", work_done_by_TDanza)

# 2. All work done before 3-25-2023 date on a Flame.

date = "2023-03-25"
flame_documents = my_collection_one.find({"Machine": "Flame", "Date of file": {"$lt": date}})

flame_users_dates = [(doc["Name of user on file"], doc["Date of file"]) for doc in flame_documents]

work_done = []
for user, date in flame_users_dates:
    work_document = my_collection_two.find_one({"Name of user on file": user, "Date of file": date})
    if work_document:
        work_done.extend(work_document["Location/Frames to fix"])


print("Work done before 3-25-2023 on a Flame:", work_done)

# 3. Work done on hpsans13 on date 3-26-2023

name = "/hpsans13"
date = "2023-03-26"
work_documents = my_collection_two.find({"Date of file": date})

work_done = []
for doc in work_documents:
    for location_frame in doc["Location/Frames to fix"]:
        if location_frame.startswith(name):
            work_done.append(location_frame)

if work_done:
    print(f"Work done on {name} on {date}:", work_done)
else:
    print(f"No work found on {name} on {date}.")

# 4. Name of all Autodesk Flame users

flame_documents = my_collection_one.find({"Machine": "Flame"})

flame_users = {doc["Name of user on file"] for doc in flame_documents}

print("Names of all Flame users:", flame_users)
