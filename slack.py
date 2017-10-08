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
        return {"text": response_text, "attachments": options}

# Slack Routes
# @app.route('/api/podcast/latest', methods=['POST'])
# def latest_episode():
#     collection = podcasts['pitpodcast'].collection
#     latest_episode = collection.find({}, sort=[('publish_date', -1)])[0]
#     return '*Latest Episode*🎙️:\n<https://productivityintech.com/pitpodcast/{}|{}>'.format(latest_episode['_id'], titlecase(latest_episode['title']))


# @app.route('/api/slack/challenge', methods=['POST'])
# def slack_connect():
#     data = request.json
#     challenge = {'challenge':data['challenge']}
#     print(data)
#     return jsonify(challenge)


# @app.route('/api/slack/goal', methods=['POST'])
# def slack_goals():
#     user_id = request.form['user_id']
#     text = request.form['text']
#     goal = Goal(user_id)
#     if text:
#         return goal.add_goal(text)
#     else:
#         return jsonify(goal.retrieve_goal())

# @app.route('/api/slack/goal/button', methods=['POST'])
# def slack_goal_buttons():
#     form = json.loads(request.form['payload'])
#     user = form['user']['id']
#     goal = Goal(user)
#     action_value = form['actions'][0]['value']
#     if action_value == 'complete':
#         return jsonify(goal.complete_goal())
#     elif action_value == 'smart':
#         response_text = {
#                 "attachments": [
#                     {
#                         "title_link": "http://www.hr.virginia.edu/uploads/documents/media/Writing_SMART_Goals.pdf",
#                         "title": "Setting Smart Goals | University of Virginia",
#                         "color": "#3394FA",
#                         "pretext": "*SMART* is an acronym to help you create Realistic and Helpful Goals.",
#                         "text":"""S-Specific
# M-Measurable
# A-Acheivable
# R-Results Focused
# T-Time-Bound"""}
#                     ]
#                 }

#         return jsonify(response_text)
