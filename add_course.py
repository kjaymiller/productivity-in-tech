from mongo import db
course_collection = db['courses']

name = input('Name of the Course: ')
desc_title = input('Description file of the Course: ')
cost = float(input('How Much is the Course: '))
total_duration = input('What is the Totat Duration of the course (use HH:MM)')
coupon_codes = input('Enter all of the coupon code ids (comma, delimited)')
pitmember_codes = ['pitmember_' + str(a) for a in coupon_codes]
video_url = input('Enter the URL of the Introduction Video: ')
mailing_list_url = input('Enter the URL of the Mailing List: ')

with open(desc_title) as f:
    desc = f.read()

data = {
    'name': name,
    'desc': desc,
    'cost': cost,
    'coupons': pitmember_codes,
    'video_url': video_url,
    'total_duration': total_duration,
    'mailing_list_url': mailing_list_url
    }

course_collection.insert_one(data)
