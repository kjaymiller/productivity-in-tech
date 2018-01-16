from blueprints import (
    app,
    mail,
    )
from flask import (
    render_template,
    redirect,
    url_for,
    Markup,
    session,
    make_response,
    Response,
    request,
    Blueprint,
    )
from bson.objectid import ObjectId
from urllib.error import HTTPError
from urllib.request import urlopen
import re
import json
import bcrypt
import pytz
from markdown import markdown
from bs4 import BeautifulSoup
import requests
from blog import blog
from load_config import load_config
from collections import Counter
from links import Links
from mailchimp_config import mailchimp_client, mailing_list_id
from models import (
    last,
    podcast_page,
    latest_episode,
    latest_post,
    )
import stripe
from titlecase import titlecase
from datetime import datetime, timedelta
from podcasts import (
    podcasts,
    )
from mongo import (
    USER_DB,
    get_pages,
    filter_by_date,
    default_sort_direction,
    )
from similar_posts import similar_posts

site_mod = Blueprint(
    'base_site',
    __name__, 
    template_folder='templates',
    )

cfg = load_config('config.yml')
STRIPE = cfg['stripe']
SLACK = cfg['SLACK_TOKEN']




def get_podcast(podcast=None):
    """ retrieves podcast from """
    if any([podcast == 'podcast', podcast == None]):
        return default_podcast

    podcast = podcasts[podcast.lower()]
    return podcast


def load_markdown_page(page, title=''):
    with open(page) as f:
        body = Markup(markdown(f.read()))
        title = titlecase(title)
    return render_template('markdown_page.html', body=body, title=title)




def interval(content):
    iterator = re.finditer(r'[\.\?\!]', content)
    preview = [x for x in filter(lambda x: x.start() < 250, iterator)][-1].start()
    return content[:preview + 1] + '..'


def render_markdown(entry, key):
    entry[key] = markdown(entry[key]) 
    return entry

def render_markup(entry, key):
    entry[key] = Markup(entry[key])
    return entry

@site_mod.route('/')
@site_mod.route('/index')
def index():
    podcast = podcasts['pitpodcast']
    episode = podcast.collection.find_one(filter_by_date(), sort=default_sort_direction)
    if episode:
        raw_podcast_post = markdown(interval(episode['content']))
        soup = BeautifulSoup(raw_podcast_post, "html.parser")
        episode['content'] = soup.text 
    blog_post = blog.collection.find_one(filter_by_date(), sort=default_sort_direction)
    if blog_post:
        blog_post['content'] = interval(blog_post['content'])

    return render_template(
        'index.html',
        podcast = podcast,
        episode = episode,
        blog_post = blog_post,
        )

@site_mod.route('/podcast')
def podcast_reroute():
    return redirect(url_for('podcast.podcast_archive'))
  
@site_mod.route('/blog')
def blog_list():
    def title_case(entry):
        entry['title'] = titlecase(entry['title'])
        return entry
    posts = list(map(title_case, blog.collection.find({}, sort=default_sort_direction)))
    return render_template(
        'blog.html',
        blog=blog,
        posts=posts,
        header=True,
        )


@site_mod.route('/blog/<lookup>')
def post(lookup=None):
    collection = blog.collection
    friendly_lookup = collection.find_one({'friendly': lookup})
    id_lookup = collection.find_one({'_id':ObjectId(lookup)})
    if friendly_lookup:
        entry = friendly_lookup
    else:
        entry = id_lookup

    content = Markup(markdown(entry['content'])) # content is stored in html
    date_format = '%a, %d %b %Y %H:%M:%S %z'
    publish_date = datetime.strftime(entry['publish_date'], date_format)
    return render_template('post.html',
        entry=entry,
        title=titlecase(entry['title']),
        content=content,
        publish_date = publish_date,
        author = entry['author'],
        header=True,
        similar = similar_posts(entry, collection))


@site_mod.route('/coaching')
@site_mod.route('/mentorship')
def coaching():
    return load_markdown_page(
        page='app/static/md/coaching.md', 
        title="Let Me Help You Get Productive",
        )


@site_mod.route('/feedback')
def feedback():
    return render_template('feedback.html')

# Redirect Pages
@site_mod.route('/fb')
@site_mod.route('/FB')
@site_mod.route('/facebook')
@site_mod.route('/Facebook')
def facebook():
    return redirect('https://facebook.com/prodintech')


@site_mod.route('/twitter')
@site_mod.route('/Twitter')
def twitter():
    return redirect('https://twitter.com/Prodintech')


@site_mod.route('/patreon')
def patreon():
    """Redirects to Patreon Page"""
    return redirect('https://patreon.com/productivityintech')


@site_mod.route('/support1')
@site_mod.route('/support-one')
@site_mod.route('/support-1')
@site_mod.route('/support%201')
@site_mod.route('/support%20one')
@site_mod.route('/paypal')
def support1():
    """Redirects to personal Paypal Page"""
    return redirect('http://bit.ly/pitsupport1')


@site_mod.route('/youtube')
@site_mod.route('/Youtube')
@site_mod.route('/YouTube')
def youtube():
    """Redirects to the PITYoutube Page"""
    return redirect('https://www.youtube.com/channel/UCw9MKaVM-8EPNyhW3VYVacQ')

@site_mod.route('/coc')
def conduct():
    return load_markdown_page('app/static/md/Code of Conduct.md', title="Productivity in Tech Code of Conduct")


@site_mod.route('/vision')
@site_mod.route('/goals')
def vision_goals():
    return load_markdown_page('app/static/md/Vision and Goals.md', "The Vision of Productivity in Tech")


@site_mod.route('/join', methods=['GET', 'POST'])
@site_mod.route('/premium', methods=['GET', 'POST'])
@site_mod.route('/support', methods=['GET', 'POST'])
def subscribe():

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
        mailchimp_client.lists.members.create(
            mailing_list_id, 
            {
            'email_address': email,
             'status': 'subscribed',
             'merge_fields': {'MEMBERSHIP':membership},
              }) 

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

@site_mod.route('/vault')
def vault():
    if 'logged_in' in session:
        return render_template('vault.html')
    return render_template(
        '/login.html', 
        message='Before you can access the vault, You will need to login.',
        redirect= 'vault')


@site_mod.route('/courses/say-no')
def say_no():
    return redirect(url_for('index'))
