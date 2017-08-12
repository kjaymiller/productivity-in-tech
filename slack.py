from datetime import datetime, timedelta
import pytz
from pymongo import ReturnDocument
from mongo import db

class Goal():
    collection = db['slack_goals']
    default_goal = "You haven't set a goal yet. Use command `\goal <enter your goal here`"

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
            return {
                    "response_type": "in_channel",
                    "text": 'Your Current Goal: _{}_ is now complete. Your previous goal will be set as the current goal'.format(goal['goal'], self.retrieve_goal()),
                    "fallback": "Okay Let me know if you need anything",
                    "callback_id": "lets_celebrate",
                    "color": "#3AA3E3",
                    "attachment_type": "default",
                    "actions":[{
                            "name": "celebrate",
                            "text": "celebrate",
                            "type": "button",
                            "value": goal['goal']
                            }]
                    }

        else:
            return self.default_goal

    def retrieve_goal(self):
        goal = self.collection.find_one({'user_id':self.user_id, 'completed':{'$exists': False}}, sort=[('goal_date', -1)])
        if goal:
            response_text = 'Your Current Goal: _{}_'.format(goal['goal'])
            options = [{
                        "response_type": "in_channel",
                        "text": "Select a Command",
                        "fallback": "Okay Let me know if you need anything",
                        "callback_id": "get_goal",
                        "color": "#3AA3E3",
                        "attachment_type": "default",
                        "actions": [
                                    {
                                        "name": "complete",
                                        "text": "Completed",
                                        "type": "button",
                                        "value": "complete"
                                        },
                                    {
                                        "name": "help",
                                        "text": "Help",
                                        "style": "danger",
                                        "type": "button",
                                        "value": "help"
                                        }
                                   ]
                        }]

        else:
            response_text = self.default_goal
            options = [{
                        "text": "Select a Command",
                        "fallback": "Okay Let me know if you need anything",
                        "callback_id": "get_goal",
                        "color": "#3AA3E3",
                        "attachment_type": "default",
                        "actions": [
                                    {
                                        "name": "smart_goals",
                                        "text": "Smart Goals",
                                        "type": "button",
                                        "value": "smart"
                                        },
                                    {
                                        "name": "help",
                                        "text": "Help",
                                        "style": "danger",
                                        "type": "button",
                                        "value": "help"
                                        }
                                   ]
                        }]
        return {"response_type": "in_channel", "text": response_text, "attachments": options}
