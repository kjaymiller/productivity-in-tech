"""This is the MailChimp config file. Use this to connect to mailchimp3

BE SURE TO EXLCUDE THIS FROM YOUR REPOSITORY
"""
from mailchimp3 import MailChimp

USERNAME = 'kjaymiller'
PASSWORD = 'f3acac0103d10afa98a9ec208c904c01-us9'

mailing_list_id = 'be1a9b82b6'

mailchimp_client = MailChimp(USERNAME, PASSWORD)