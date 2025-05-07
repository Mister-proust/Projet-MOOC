from pymongo import MongoClient

# Requires the PyMongo package.
# https://api.mongodb.com/python/current

client = MongoClient("mongodb://localhost:27017/")
filter={}
project={
    'content.id': 1, 
    'content.course_id': 1, 
    'content.username': 1,
    'content.children': 1,
    'content.depth': 1
}

result = client['MOOC']['forum'].find(
  filter=filter,
  projection=project
)

def stevefunk(content):
    username = content.get("username", "")
    courseid = content.get("course_id", "")
    id = content.get("id", "")
    children = content.get("children", [])
    depth = content.get("depth", "?")
    print(f"{depth} {id} {courseid:80} {username}")
    for doc in children:
        stevefunk(doc)

for doc in result:
    content = doc["content"]
    print("---------------------------------------------------------------------------------------------------------------------------------------------")
    stevefunk(content)
