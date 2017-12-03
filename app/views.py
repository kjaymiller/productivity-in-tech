from app import app
from flask import (
    render_template,
    redirect,
    url_for,
    Markup,
    session,
    make_response,
    Response,
    request,
    )
from bson.objectid import ObjectId
from urllib.error import HTTPError
from urllib.request import urlopen
import re
import json
import pytz
from bcrypt import hashpw, gensalt
from markdown import markdown
import stripe
from mailchimp_config import mailchimp_client, mailing_list_id
import requests
from blog import blog
from load_config import cfg
from mongo import userdb_collection
from collections import Counter
from links import Links

from models import (
    last,
    podcast_page,
    latest_episode,
    latest_post,
    )
from titlecase import titlecase
from datetime import datetime
from podcasts import podcasts

STRIPE = cfg['stripe']
stripe.api_key = STRIPE['API_KEY']
SLACK = cfg['SLACK_TOKEN']
default_podcast = podcasts['pitpodcast']
message_url = 'courses/say-no'
no_shownotes = "I'm sorry but shownotes have not been completed for this episode"
def less_than_now():
  return {'publish_date': {'$lt': datetime.now(pytz.utc)}}

def get_pages(collection, page, limit):
    """Creates Page Logic for Archives"""
    page_index = (page - 1) * limit
    start_id = collection.find(less_than_now(), 
                                sort=[('publish_date', -1)])[page_index]
    return collection.find({'publish_date':{'$lte':start_id['publish_date']}}, 
                            sort=[('publish_date', -1)]).limit(limit)


def get_podcast(podcast=None):
    """ retrieves podcast from """
    if any([podcast == 'podcast', podcast == None]):
        return default_podcast

    podcast = podcasts[podcast.lower()]
    return podcast


def load_markdown_page(page, title):
    with open(page) as f:
        body = Markup(markdown(f.read()))
        title = titlecase(title)
    return render_template('markdown_page.html', body=body, title=title)


def similar_posts(entry, collection):
        posts = []
        for tag in entry.get('tags', []):
            entries = collection.find({'tags': tag})
            posts.extend([('./'+ str(x['_id']), x['title']) for x in entries])

        strip_post = filter(lambda x: x[1] != entry['title'], posts)
        return Counter(strip_post).most_common(4)


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

@app.route('/')
@app.route('/index')
def index():
    podcast = get_podcast()
    episode = podcast.collection.find_one(less_than_now(), sort=[('publish_date', -1)])
    episode['content'] = interval(episode['content'])

    blog_post = blog.collection.find_one({}, sort=[('publish_date', -1)])
    blog_post['content'] = interval(blog_post['content'])

    message_cookie = request.cookies.get('message', None)
    if message_cookie == 'closed':
        template = render_template('index.html',
                    podcast = podcast,
                    episode = episode,
                    blog_post = blog_post,
                    )
    else:
        with open('banner_message.md') as f:
            message = {
                    'url': message_url,
                    'text': Markup(markdown(f.read()))
                    }
        template = render_template('index.html',      
                    podcast = podcast,   
                    episode = episode,
                    blog_post = blog_post,
                    message=message)

    resp = make_response(template)
    return resp

  
@app.route('/<podcast>/latest')
@app.route('/<podcast>/last')
@app.route('/<podcast>/<int:episode_number>')
@app.route('/<podcast>/<id>')
def play(podcast, id=None, episode_number=None):
    podcast = get_podcast(podcast)
    collection = podcast.collection
    last_episode = last(collection)
    if episode_number:
        episode = collection.find_one({'episode_number': episode_number})
    elif id:
        episode = collection.find_one({'_id': ObjectId(id)})
    else:
        episode = last_episode

    shownotes = Markup(markdown(episode.get('content', no_shownotes)))

    return render_template('play.html',
                           episode=episode,
                           shownotes=shownotes,
                           podcast=podcast,
                           header=True,
                           other_posts=similar_posts(episode, collection))


@app.route('/<podcast>/ep/<int:episode_number>')
def episode_by_episode_number(podcast, episode_number):
    podcast = get_podcast(podcast)
    collection = podcast.collection
    episodes = collection.find(less_than_now(), sort=[('publish_date', 1)])
    max_episode_number = episodes.count()
    
    if episode_number <= max_episode_number:
        episode = episodes[episode_number - 1]
    
    else:
        episode = episodes[max_episode_number - 1]

    shownotes = Markup(markdown(episode.get('content', no_shownotes)))
    return render_template('play.html',
                            episode=episode,
                            shownotes=shownotes,
                            podcast=podcast,
                            header=True,
                            other_posts=similar_posts(episode, collection))


@app.route('/pitmaster')
@app.route('/<podcast>')
@app.route('/podcast')
@app.route('/<podcast>/list')
@app.route('/<podcast>/archive')
def podcast_archive(limit=10, podcast=None):
    podcast = get_podcast(podcast)
    page = int(request.args.get('page', 1))
    collection = podcast.collection
    episodes = get_pages(collection, page, limit)
    max_page = collection.find(less_than_now()).count()/limit
    return render_template('podcast_archive.html', podcast=podcast,
                            episodes=episodes, page=page, 
                            max_page=max_page, header=True)

@app.route('/blog')
def blog_list():
    def title_case(entry):
        entry['title'] = titlecase(entry['title'])
        return entry
    posts = list(map(title_case, blog.collection.find({}, sort=[('publish_date', -1)])))
    return render_template('blog.html', blog=blog, posts=posts, header=True)

@app.route('/blog/<lookup>')
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


@app.route('/coaching')
def coaching():
    return load_markdown_page('app/static/md/coaching.md', title="Let Me Help You Get Productive")
@app.route('/feedback')
def feedback():
    return render_template('feedback.html')

# Redirect Pages
@app.route('/fb')
@app.route('/FB')
@app.route('/facebook')
@app.route('/Facebook')
def facebook():
    return redirect('https://facebook.com/prodintech')


@app.route('/twitter')
@app.route('/Twitter')
def twitter():
    return redirect('https://twitter.com/Prodintech')


@app.route('/patreon')
def patreon():
    """Redirects to Patreon Page"""
    return redirect('https://patreon.com/productivityintech')


@app.route('/support1')
@app.route('/support-one')
@app.route('/support-1')
@app.route('/support%201')
@app.route('/support%20one')
@app.route('/paypal')
def support1():
    """Redirects to personal Paypal Page"""
    return redirect('http://bit.ly/pitsupport1')


@app.route('/youtube')
@app.route('/Youtube')
@app.route('/YouTube')
def youtube():
    """Redirects to the PITYoutube Page"""
    return redirect('https://www.youtube.com/channel/UCw9MKaVM-8EPNyhW3VYVacQ')

@app.route('/coc')
def conduct():
    return load_markdown_page('app/static/md/Code of Conduct.md', title="Productivity in Tech Code of Conduct")

@app.route('/vision')
@app.route('/goals')
def vision_goals():
    return load_markdown_page('app/static/md/Vision and Goals.md', "The Vision of Productivity in Tech")


@app.route('/subscribe/<coupon_code>')
@app.route('/premium/<coupon_code>')
@app.route('/join/<coupon_code>')
@app.route('/support/<coupon_code>')
@app.route('/subscribe')
@app.route('/join')
@app.route('/premium')
@app.route('/support')
def subscribe(coupon_code='', coupon=None, header=None):
    amounts = {'annual': 300,
               'monthly': 30}
    with open('coupon_codes.json') as jsonfile:
        coupons = json.load(jsonfile)

    if coupon_code.lower() in coupons.keys():
        coupon = {**coupons['default'], 
                    **coupons[coupon_code.lower()]}
        header = Markup(coupon['header'])

    return render_template('subscribe.html',
                           data_key=STRIPE['DATA_KEY'],
                           coupon=coupon,
                           header=header,
                           amounts=amounts)


@app.route('/payment/<plan>/<coupon>', methods=['POST'])
@app.route('/payment/<plan>', methods=['POST'])
def payment_successful(plan, coupon=None):
    if  userdb_collection.find_one({'email': email, 'password':{'$exists': True}}):
        return 'This email address is already registered.'
    
    email = request.form['stripeEmail']

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


@app.route('/courses')
def courses():
    return render_template('courses.html')


@app.route('/courses/Say-No')
@app.route('/courses/say-no')
def say_no():
    return load_markdown_page('app/static/md/no_course_landing.md', title='Learn How to Tell Your Boss, Your Friends, and Your Family "No"')


@app.route('/blog/feed/feed.xml')
def blog_rss():
    raw_posts = blog.collection.find(less_than_now(), 
                                    sort=[('publish_date', -1)], 
                                    limit=10)

    entries = [render_markdown(x, 'content') for x in raw_posts]
    updated_date = entries[0]['publish_date']
    website = cfg['website']
    atom_xml = render_template('blog.xml', 
                            entries= entries, 
                            website = website,
                            updated_date = updated_date,
                            year = datetime.now().year
                            )
    response = Response(atom_xml, contentxml)
    return response


@app.route('/vault')
def vault():
    return render_template('vault.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']    
        user_entry = userdb_collection.find_one({'email': email})

        if user_entry:
            if hashpw(request.form['password'], user_entry['password']) == user_entry['password']:
                return 'Thanks for Logging in!'
            
            else:
                return render_template('login.html', error_message='Wrong Password, Please Try Again!')
        else: 
            return render_template('login.html', error_message='No Account can be found for this email. Please Register and Create a new one!')
    return render_template('login.html')

def set_password():
    email = session['email']
    if not userdb_collection.find_one({'email': email, 'password':{'$exists': True}}):
        return render_template('register.html', email=email)

    if userdb_collection.find_one({'email': email}):
        return '<h1>an account for this email already exists</h1>'

    else:
        return abort(401)

@app.route('/register', methods=['POST'])
def register():
    password = hashpw(request.form['password'], gensalt())
    email = session['email']

    userdb_collection.update({'email': email}, {'$set':{'password': password}})
    return render_template('payment_successful.html')
