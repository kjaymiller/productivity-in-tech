from datetime import datetime, timedelta
from mongo import db


target_goal_day = 0

class Goal():
    collection = db['slack_goals']
    goal_date = datetime.now() - timedelta(today - target_goal_day)

    def add_goal(self, user, goal):
        if not self.collection.find_one({'user':user, 'goal_date':goal_date}):
            data = {'goal': goal,
                    'goal_date': self.goal_date,
                    'user': user}
            self.collection.insert_one(data)
        else:
            self.collection.update({'user': user, 'goal_date': self.goal_date},
                    {'$set':{'goal': goal}})
        return 'Goal Successfully Added: _{}_'.format(goal)

    def retrieve_goal(self, user):
        goal = goal.collection.find_one({'user':self.user, 'goal_date':self.goal_date})
        if goal_text:
            return 'Your Current Goal: _{}_'.format(goal['goal'])
        else:
            return "You haven't set a goal for this week"
