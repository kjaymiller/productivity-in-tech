from datetime import datetime, timedelta
from mongo import db

today = datetime.today().weekday()
target_goal_day = 0

class Goal():
    collection = db['slack_goals']

    def add_goal(self, user_id, goal):
        data = {'goal': goal,
                'goal_date': self.goal_date,
                'user_id': user_id}
        self.collection.insert_one(data)
        return 'Goal Successfully Added: _{}_'.format(goal)

    def retrieve_goal(self, user_id):
        goal = self.collection.find_one({'user_id':user_id}, sort=[('goal_date', -1)])
        if goal:
            return 'Your Current Goal: _{}_'.format(goal['goal'])
        else:
            return "You haven't sat a goal yet"
