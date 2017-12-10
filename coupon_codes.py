"""A Dictionary File That Contains the coupon name, a description of the 
coupon and the stripe coupon it corresponds to"""
from flask import Markup

coupons = {'talkpython': {
        'code':{
                'annual':'save200',
                'monthly': 'save20'},
        'amounts': {'annual': 100,
                    'monthly': 10},
        'header': Markup('<img src="http://productivityintech.com/files/images/Talk Python To Me.png" height="50px">TalkPython Listeners, Join the PIT Family Today'),
		'thanks':'Thank you Talk Python Listener! Your ~2/3 Discount \
FOR LIFE has been applied!'
            },

        'friends_and_family': {
        'code':{
                'annual':'save200',
                'monthly': 'save20'},
        'amounts': {'annual': 100,
                    'monthly': 10},
        'header': Markup("You're Awesome! \
        		We'd Love it if you joined the PIT Family Today! 💙"),
		'thanks':'We want to give you a $20/mnt off FOR LIFE'
            },

        'eatsleepcode': {
        'code':{
                'annual':'save200',
                'monthly': 'save20'},
        'amounts': {'annual': 100,
                    'monthly': 10},
        'header': Markup("You're Awesome! \
        		Eat Sleep Code Listeners, We'd love it if you joined the PIT Family Today! 💙"),
		'thanks':'We want to give you a $20/mnt off FOR LIFE'
            },
		
		'friends_and_family': {
        'code':{
                'annual':'save200',
                'monthly': 'save20'},
        'amounts': {'annual': 100,
                    'monthly': 10},
        'header': Markup("You're Awesome! \
        		IT Career Energizer Podcast Listeners, We'd Love it if you joined the PIT Family Today! 💙"),
		'thanks':'We want to give you a $20/mnt off FOR LIFE'
            }
        }

