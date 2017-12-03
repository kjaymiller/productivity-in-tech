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
from bcrypt import hashpw, gensalt
import requests
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
def login(error_message=''):
    if request.method == 'POST':
        email = request.form['email']    
        user_entry = userdb_collection.find_one({'email': email})

        if user_entry:
            if hashpw(request.form['password'], user_entry['password']) == user_entry['password']:
                session['logged_in'] = True
                return redirect(url_for('vault'))

            
            else:
                error_message = 'Wrong Password, Please Try Again!'
        else: 
            error_message ='No Account can be found for this email. Please Register and Create a new one!'
    return render_template('login.html', error_message=error_message)

def set_password():
    email = session['email']
    if not userdb_collection.find_one({'email': email, 'password':{'$exists': True}}):
        return render_template('/register.html', email=email)

    if userdb_collection.find_one({'email': email}):
        return '<h1>an account for this email already exists</h1>'

    else:
        return abort(401)

@users.route('/register', methods=['POST'])
def register():
    password = hashpw(request.form['password'], gensalt())
    email = session['email']
    session['logged_in'] = True 
    userdb_collection.update({'email': email}, {'$set':{'password': password}})
    return render_template('payment_complete.html')

@users.route('/reset', methods=['GET','POST'])
def reset(email=''):
    msg = Message("Hello",
                  sender="jay@productivityintech.com",
                  recipients=["kjaymiller@gmail.com"])
    msg.body = "<b>Hi There!!</b>"
    mail.send(msg)