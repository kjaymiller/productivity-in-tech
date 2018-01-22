from blueprints import app, mail
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
from load_config import load_config
from mailchimp_config import mailchimp_client, mailing_list_id
from mongo import USER_DB

users_mod = Blueprint(
    'users',
    __name__, 
    template_folder='templates',
    )

users_collection = USER_DB['users']
cfg = load_config('config.yml')
STRIPE = cfg['stripe']
stripe.api_key = STRIPE['API_KEY']
SLACK = cfg['SLACK_TOKEN']

@users_mod.route('/login', methods=['GET', 'POST'])
def login(message=''):
    message = request.args.get('message', message)
    if request.method == 'POST':
        email = request.form['email']    
        user_entry = users_collection.find_one({'email': email})

        if user_entry:
            if bcrypt.checkpw(request.form['password'].encode('utf-8'), user_entry['password']):
                session['logged_in'] = True
                return redirect(url_for('vault'))
            
            else:
                message = 'Wrong Password, Please Try Again!'
        else: 
            message ='No Account can be found for this email. Please Register and Create a new one!'
    return render_template('login.html', message=message)


def set_password():
    email = session['email']
    if not users_collection.find_one({'email': email, 'password':{'$exists': True}}):
        return render_template('register.html')

    if users_collection.find_one({'email': email}):
        return '<h1>an account for this email already exists</h1>'

    else:
        return abort(401)


@users_mod.route('/register', methods=[ 'GET', 'POST'])
def register():
    if request.method == 'POST':
        email = session.get('email', request.args.get('email'))

        if request.form['password'] != request.form['confirm_password']:
            message = 'passwords do not match'
            return render_template('register.html', email=email, message=message)
        
        password = bcrypt.hashpw(request.form['password'], bcrypt.gensalt())
        session['logged_in'] = True 
        users_collection.update({'email': email}, {'$set':{'password': password}})
        return render_template('payment_complete.html')
    return render_template('register.html')

@users_mod.route('/reset', methods=['GET','POST'])
def reset_account(email='', message=''):
    if request.method == 'POST':
        email = request.form['email']
    
        if not users_collection.find_one({'email': email, 'password':{'$exists': True}}):
            message = 'Invalid Email Address Entered'
            return render_template('send_password.html', message=message)

        plain_key = ''.join(random.SystemRandom().choice(string.ascii_uppercase + string.digits) for _ in range(6))
        hash_key = bcrypt.hashpw(plain_key, bcrypt.gensalt())
        key_expiration = datetime.now() + timedelta(minutes=15)
        users_collection.update(
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


@users_mod.route('/change/password', methods=['GET', 'POST'])
def change_pwd():            
    key = session.get('key', '')   
    key = request.args.get('key', key)
    email = session.get('email', '')
    email = request.args.get('email', email)
    message = request.args.get('message')
    user = users_collection.find_one({
        'email': email,
        'key_expiration': {'$gt': datetime.now()},
        'password': {'$exists': True},
        })
    
    if not user:
        message = "Error: Either this email hasn't requested a password change or the request has expired!"
        users_collection.update({'email': email}, {'$unset': {'key_check': 1}})
        return render_template('reset.html', message=message)

    if not bcrypt.checkpw(key, user['temp_key']):
        message = f'{key} Invalid URL. Did your key expire?'
        users_collection.update(
            {'email': email}, 
            {'$unset': {'temp_key': True, 'key_expiration': True}})
        return render_template('send_password.html', message=message, email=email)

    if request.method == 'POST':
       
        if request.form['password'] != request.form['confirm_password']:
            message = 'passwords do not match'
            return render_template('reset.html', message=message, email=email)

        password = bcrypt.hashpw(request.form['password'], bcrypt.gensalt())
        users_collection.update(
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

@users_mod.route('/join')
def subscribe():
    """ SIGNUP NEW USERS """
    if request.method == 'POST':
        password = request.form['password']
        confirm = request.form['confirm-password']
        email = request.form['email']
        token = request.form['token_field']
        membership = request.form['membership-option']

        def return_error(message):
            return render_template(
                'subscribe2.html',
                data_key=STRIPE['DATA_KEY'], 
                error = f'Your card could not be charged. \
                {message}.',
                )

        # Check that all fields are populated
        for field in (password, confirm, email, token, membership):
            if not field:
                return return_error(f'{field} must be populated')

        # Check that user doesn't already exist
        if USER_DB['user'].find_one({'email': email}):
            return redirect(url_for('users.login', message='User Account Already Exists'))

        if password != confirm:
            return return_error('Passwords do not match.')

        # All Checks Pass. Add users to MailChimp, Stripe, and User Database
        try: # Will error Out if they're already on the list
            mailchimp_client.lists.members.create(
                mailing_list_id, 
                {
                'email_address': email,
                'status': 'subscribed',
                'merge_fields': {'MEMBERSHIP':membership},
                })

        except:
            pass

        customer =  stripe.Customer.create(
            email=email,
            source=token,
            )

        stripe.Subscription.create(
            customer=customer['id'], 
            items=[{'plan': membership}],
            trial_end=datetime.now() + timedelta(days=14)
            )        

        USER_DB['user'].insert({
            'email': email,
            'password': bcrypt.hashpw(password, bcrypt.gensalt()),
            'customer_id': customer['id'],
            'membership_type': membership,
            })

        # Send Users Slack Invite
        requests.post('https://slack.com/api/users.admin.invite?token={}&email={}&resend=true'.format(SLACK, email))
        return render_template('registration_successful.html')

    # Get Request    
    return render_template('subscribe2.html',
                           data_key=STRIPE['DATA_KEY'])

