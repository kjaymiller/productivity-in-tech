from app import app, mail
from flask import (
    render_template,
    redirect,
    url_for,
    session,
    request,
    Blueprint,
    )
from flask_mail import Message
import bcrypt
from datetime import datetime, timedelta
import random
import requests
import string
import stripe
from load_config import cfg
from mailchimp_config import mailchimp_client, mailing_list_id
from mongo import userdb_collection

users = Blueprint(
    'users',
    __name__, 
    template_folder='templates',
    )

STRIPE = cfg['stripe']
stripe.api_key = STRIPE['API_KEY']
SLACK = cfg['SLACK_TOKEN']

@users.route('/payment/<plan>/<coupon>', methods=['POST'])
@users.route('/payment/<plan>', methods=['POST'])
def payment_successful(plan, coupon=None):
    email = request.form['stripeEmail']

    if  userdb_collection.find_one({'email': email, 'password':{'$exists': True}}):
        return 'This email address is already registered.'
    
    # Create Customer Account in Stripe
    customer = stripe.Customer.create(
        email=email,
        source=request.form['stripeToken']
        )

    # Create Subscription Based on Plan
    if coupon:
        subscription = stripe.Subscription.create(
            customer=customer.id,
            coupon=coupon,
            plan=plan)

    else:
        subscription = stripe.Subscription.create(
                    customer=customer.id,
                    plan=plan)

    # Add User to Mailchimp Premium Users List
    # mailchimp_client.lists.members.create(mailing_list_id, {'email_address': email, 'status':'subscribed'})

    #Send Users 
    requests.post('https://slack.com/api/users.admin.invite?token={}&email={}&resend=true'.format(SLACK, email))
    userdb_collection.insert_one({'email': email, 'customer_id': customer.id})
    session['email'] = email
    return set_password()

@users.route('/login', methods=['GET', 'POST'])
def login(message=''):
    message = request.args.get('message', message)
    if request.method == 'POST':
        email = request.form['email']    
        user_entry = userdb_collection.find_one({'email': email})

        if user_entry:
            if bcrypt.checkpw(request.form['password'], user_entry['password']):
                session['logged_in'] = True
                return redirect(url_for('vault'))
            
            else:
                message = 'Wrong Password, Please Try Again!'
        else: 
            message ='No Account can be found for this email. Please Register and Create a new one!'
    return render_template('login.html', message=message)


def set_password():
    email = session['email']
    if not userdb_collection.find_one({'email': email, 'password':{'$exists': True}}):
        return render_template('register.html', email=email)

    if userdb_collection.find_one({'email': email}):
        return '<h1>an account for this email already exists</h1>'

    else:
        return abort(401)


@users.route('/register', methods=['POST'])
def register():
    password = bcrypt.hashpw(request.form['password'], bcrypt.gensalt())
    email = session['email']
    session['logged_in'] = True 
    userdb_collection.update({'email': email}, {'$set':{'password': password}})
    return render_template('payment_complete.html')


@users.route('/reset', methods=['GET','POST'])
def reset_account(email='', message=''):
    if request.method == 'POST':
        email = request.form['email']
    
        if not userdb_collection.find_one({'email': email, 'password':{'$exists': True}}):
            message = 'Invalid Email Address Entered'
            return render_template('send_password.html', message=message)

        plain_key = ''.join(random.SystemRandom().choice(string.ascii_uppercase + string.digits) for _ in range(6))
        hash_key = bcrypt.hashpw(plain_key, bcrypt.gensalt())
        key_expiration = datetime.now() + timedelta(minutes=15)
        userdb_collection.update(
            {'email': email}, 
            {'$set':{'temp_key':hash_key, 'key_expiration': key_expiration}},
            )

        msg = Message(
            "Did you request a password change?",
            sender="jay@productivityintech.com",
            recipients=["kjaymiller@gmail.com"],
            )
        
        msg.html = '''
<h1>Did you just request a Password change? </h1>
<h4>Hi There!!</h4>
<p>We just recieved a request to reset the password for this account. 
If it wasn't you then don't panic. 
The request requires the fancy little key that expires 15 minutes from the time it was submitted. 
That key is include in the link below. 
(also it's hashed in our database and if they try to guess it, the key deletes itself and you have to start over.)</p>

<p>If you do need to change your password click this one-time use link below and enter your new password (twice) into the new password field(s)</p> <br><br>\
<a href="http://localhost:5000/users/change/password?key={0}&email={1}">https://productivityintech.com/users/change/password?key={0}&email={1}</a>

Thanks again for being a premium member. Hope to talk to you soon!<br>
Jay!
'''.format(plain_key, email)
        mail.send(msg)
        message = 'An Email Confirmation has been sent.'
        return redirect(url_for('users.login', message=message))
    return render_template('send_password.html', email=email)


@users.route('/change/password', methods=['GET', 'POST'])
def change_pwd():            
    key = session.get('key', '')   
    key = request.args.get('key', key)
    email = session.get('email', '')
    email = request.args.get('email', email)
    message = request.args.get('message')
    user = userdb_collection.find_one({
        'email': email,
        'key_expiration': {'$gt': datetime.now()},
        'password': {'$exists': True},
        })
    
    if not user:
        message = "Error: Either this email hasn't requested a password change or the request has expired!"
        userdb_collection.update({'email': email}, {'$unset': {'key_check': 1}})
        return render_template('reset.html', message=message)

    if not bcrypt.checkpw(key, user['temp_key']):
        message = f'{key} Invalid URL. Did your key expire?'
        userdb_collection.update(
            {'email': email}, 
            {'$unset': {'temp_key': True, 'key_expiration': True}})
        return render_template('send_password.html', message=message, email=email)

    if request.method == 'POST':
        password = bcrypt.hashpw(request.form['password'], bcrypt.gensalt())
        userdb_collection.update(
            {'email': email}, 
            {
            '$set':{'password':password}, 
            '$unset': {'key_check': True, 'key_expiration': True},
            })
   
        message = 'Your Password has been changed'
        session.pop('key')
        return redirect(url_for('users.login', message=message))

    session['key'] = key
    session['email'] = email
    return render_template('reset.html', message=message, email=email)