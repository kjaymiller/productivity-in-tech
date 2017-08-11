from datetime import datetime, timedelta
import pytz
from pymongo import ReturnDocument
from mongo import db

class Goal():
    collection = db['slack_goals']
    def __init__(self, user_id):
        self.user_id = user_id

    def add_goal(self, goal):
        data = {'goal': goal,
                'goal_date': datetime.now(),
                'user_id': self.user_id}
        self.collection.insert_one(data)
        return 'Goal Successfully Added: _{}_'.format(goal)

    def complete_goal(self):
        goal = self.collection.find_one_and_update({'user_id':self.user_id, 'completed':{'$exists': False}},{'$set':{'completed':datetime.now(pytz.utc)}}, sort=[('goal_date', -1)], return_document=ReturnDocument.AFTER)
        if goal:
            return 'Your Current Goal: _{}_ is now complete. Your previous goal will be set as the current goal'.format(goal['goal'], self.retrieve_goal())
        else:
            return "You haven't sat a goal yet"

    def retrieve_goal(self):
        goal = self.collection.find_one({'user_id':self.user_id, 'completed':{'$exists': False}}, sort=[('goal_date', -1)])
        if goal:
            return 'Your Current Goal: _{}_'.format(goal['goal'])
        else:
            return "You haven't sat a goal yet"
