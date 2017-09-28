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
            }
        }