from mongo import db
from markdown import markdown

course_collection = db['courses']

add_course(data):
    return course_collection.insert_one(data)
