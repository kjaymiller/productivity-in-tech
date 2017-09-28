from app import app
from flask import (render_template,
                   redirect,
                   url_for,
                   Markup,
                   make_response,
                   request,
                   jsonify,
                   abort)
from bson.objectid import ObjectId
from urllib.error import HTTPError
from urllib.request import urlopen
import re
import json
import pytz
from markdown import markdown
import stripe
from mailchimp_config import mailchimp_client, mailing_list_id
import requests
from blog import blog

# UnComment if Testing
from config import STRIPE_TEST_API_KEY as STRIPE_API_KEY
from config import STRIPE_TEST_DATA_KEY as STRIPE_DATA_KEY

#UnCommunt if Live
# from config import STRIPE_API_KEY
# from config import STRIPE_DATA_KEY

from config import SLACK_TOKEN
from collections import Counter
from links import RSS, Google, ITunes, Overcast, PocketCasts
from models import (last,
                    podcast_page,
                    latest_episode,
                    latest_post)
from slack import Goal
from titlecase import titlecase
from datetime import datetime
from podcasts import podcasts
from coupon_codes import coupons

stripe.api_key = STRIPE_API_KEY


def remaining_members(total):
        return total - len(stripe.Customer.list()['data'])


def load_markdown_page(page, title):
    with open(page) as f:
        body = Markup(markdown(f.read()))
        title = titlecase(title)
    return render_template('markdown_page.html', body=body, title=title)


def banner_message():
    """Loads the Banner Message at the Top of the Site
This is for site wide alerts. I may load this into a text file later on"""
    message = '<h2><a class="white" href="courses/say-no">Learn more about our upcoming "Learn to Say No Course"</a></h2>'
    return message


def similar_posts(entry, collection):
        posts = []
        for tag in entry.get('tags', []):
            entries = collection.find({'tags': tag})
            posts.extend([('./'+ str(x['_id']), x['title']) for x in entries])

        strip_post = filter(lambda x: x[1] != entry['title'], posts)
        return Counter(strip_post).most_common(4)

@app.route('/podcast')
def list_podcasts():
    return redirect(url_for('podcast_archive', podcast='pitpodcast'))

@app.route('/')
@app.route('/index')
def index():
    latest_podcast = []

    for podcast in podcasts:
        collection = podcasts[podcast].collection
        recent_episode = collection.find({}, sort=[('publish_date', -1)])[0]
        recent_episode['podcast'] = podcasts[podcast]
        recent_episode['links'] = podcasts[podcast].links
        latest_podcast.append(recent_episode)

        collection = blog.collection
        recent_posts = (collection.find_one({}, sort=[('publish_date', -1)]))
        content = recent_posts['content']
        interval = re.finditer(r'[\.\?\!]', content)
        preview_mark = [x.start() for x in interval if x.start() > 140][0] + 1
        post_preview = Markup(markdown(content[:preview_mark] + '...'))
        message_cookie = request.cookies.get('message', None)

        if message_cookie == 'closed':
            template = render_template('index.html',
                        latest_podcast=latest_podcast,
                        posts=recent_posts,
                        post_preview=post_preview)
        else:
            message = Markup(banner_message())
            template = render_template('index.html',
                        latest_podcast=latest_podcast,
                        posts=recent_posts,
                        post_preview=post_preview,
                        message=message)

        resp = make_response(template)
        return resp

@app.route('/<podcast>/latest')
@app.route('/<podcast>/last')
@app.route('/<podcast>/<int:episode_number>')
@app.route('/<podcast>/<id>')
def play(podcast, id=None, episode_number=None):
    if podcast == 'podcast':
        podcast = 'pitpodcast'
    podcast = podcasts[podcast.lower()]
    collection = podcast.collection
    last_episode = last(collection)
    if episode_number:
        episode = collection.find_one({'episode_number': episode_number})
    elif id:
        episode = collection.find_one({'_id': ObjectId(id)})
    else:
        episode = last_episode

    no_shownotes = "I'm sorry but shownotes have not been completed for this episode"
    shownotes = Markup(markdown(episode.get('content', no_shownotes)))

    return render_template('play.html',
                           episode=episode,
                           shownotes=shownotes,
                           last=last_episode,
                           podcast=podcast,
                           header=True,
                           other_posts=similar_posts(episode, collection))

@app.route('/<podcast>')
@app.route('/podcast')
@app.route('/<podcast>/list')
@app.route('/<podcast>/archive')
def podcast_archive(podcast):
    podcast = podcasts[podcast.lower()]
    collection=podcast.collection
    episodes = list(collection.find({'publish_date':
                                    {'$lt': datetime.now(pytz.utc)}},
                                    sort=[('publish_date', -1)]))
    return render_template('podcast_archive.html', podcast=podcast,
                            episodes=episodes, header=True)

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

@app.route('/guests')
def guests():
    guest_list = [guest for guest in guestlist.find()]
    print(guest_list)
    return render_template('guestlist.html', guest_list=guest_list)

@app.route('/friends')
def friends_of_show():
    friends = friends_coll.find()
    return render_template('friends.html', friends=friends, header=True)

@app.route('/live')
def live():
    url = 'http://productivityintech.com:8155/pitest'
    json_stats_url = 'http://productivityintech.com:8155/status-json.xsl'
    title = no_episode = None
    try:
        urlopen(url, timeout=1)
        with urlopen(json_stats_url) as json_stats:
            json_info = json.loads(json_stats.read().decode('utf-8'))
            title = json_info['icestats']['source']['server_name']
        is_live = True

    except HTTPError:
        is_live = False
        with open('app/static/md/no_episode.md') as f:
            no_episode = Markup(markdown(f.read()))

    return render_template('live.html',
            is_live=is_live,
            title=titlecase(title),
            no_episode=no_episode)

@app.route('/community')
def join():
    return render_template('join.html', header=True)

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

"""
@app.route('/courses')
@app.route('/course')
def all_courses():
    return render_template('courses.html')


@app.route('/courses/my')
def my_courses():
    pass


# APIs
#get the current podcast episode count
@app.route('/api/web/<podcast>/length')
def count_podcast_length(podcast):
    podcast = collections[podcast.lower()]
    collection = podcast.collection
    return str(last(collection))
"""

@app.route('/api/podcast/latest', methods=['POST'])
def latest_episode():
    collection = podcasts['pitpodcast'].collection
    latest_episode = collection.find({}, sort=[('publish_date', -1)])[0]
    return '*Latest Episode*🎙️:\n<https://productivityintech.com/pitpodcast/{}|{}>'.format(latest_episode['_id'], titlecase(latest_episode['title']))


@app.route('/api/slack/challenge', methods=['POST'])
def slack_connect():
    data = request.json
    challenge = {'challenge':data['challenge']}
    print(data)
    return jsonify(challenge)


@app.route('/api/slack/goal', methods=['POST'])
def slack_goals():
    user_id = request.form['user_id']
    text = request.form['text']
    goal = Goal(user_id)
    if text:
        return goal.add_goal(text)
    else:
        return jsonify(goal.retrieve_goal())

@app.route('/api/slack/goal/button', methods=['POST'])
def slack_goal_buttons():
    form = json.loads(request.form['payload'])
    user = form['user']['id']
    goal = Goal(user)
    action_value = form['actions'][0]['value']
    if action_value == 'complete':
        return jsonify(goal.complete_goal())
    elif action_value == 'smart':
        response_text = {
                "attachments": [
                    {
                        "title_link": "http://www.hr.virginia.edu/uploads/documents/media/Writing_SMART_Goals.pdf",
                        "title": "Setting Smart Goals | University of Virginia",
                        "color": "#3394FA",
                        "pretext": "*SMART* is an acronym to help you create Realistic and Helpful Goals.",
                        "text":"""S-Specific
M-Measurable
A-Acheivable
R-Results Focused
T-Time-Bound"""}
                    ]
                }

        return jsonify(response_text)

@app.route('/pitmaster')
def pitmaster():
    links = [ITunes('https://itunes.apple.com/us/podcast/productivity-in-tech-master/id1176381857?mt=2'),
            Google('https://play.google.com/music/listen#/ps/I235y6zisqje22eagcm2mhf2ewm'),
            Overcast('https://overcast.fm/itunes1176381857/productivity-in-tech-master-feed'),
            PocketCasts('https://play.pocketcasts.com/web/podcasts/index#/podcasts/show/81a7b290-8dc6-0134-90a4-3327a14bcdba'),
            RSS('feed://productivityintech.com/files/feed.xml')]
    return render_template('pitmaster.html', links=links)

@app.route('/coc')
def conduct():
    return load_markdown_page('app/static/md/Code of Conduct.md', title="Productivity in Tech Code of Conduct")

@app.route('/vision')
@app.route('/goals')
def vision_goals():
    return load_markdown_page('app/static/md/Vision and Goals.md', "The Vision of Productivity in Tech")


@app.route('/subscribe/<coupon>')
@app.route('/premium/<coupon>')
@app.route('/join/<coupon>')
@app.route('/support/<coupon>')
@app.route('/subscribe')
@app.route('/join')
@app.route('/premium')
@app.route('/support')
def subscribe(coupon=None):
    amounts = {'annual': 300,
               'monthly': 30}

    if coupon:
        coupon = coupons[coupon.lower()]

    return render_template('subscribe.html',
                           data_key=STRIPE_DATA_KEY,
                           coupon=coupon,
                           amounts=amounts)


@app.route('/payment/<plan>/<coupon>', methods=['POST'])
@app.route('/payment/<plan>/', methods=['POST'])
def payment_successful(plan, coupon=None):
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
    mailchimp_client.lists.members.create(mailing_list_id, {'email_address': email, 'status':'subscribed'})

    #Send Users 
    requests.post('https://slack.com/api/users.admin.invite?token={}&email={}&resend=true'.format(SLACK_TOKEN, email))
    return render_template('payment_complete.html')


@app.route('/courses/Say-No')
@app.route('/courses/say-no')
def say_no():
    return load_markdown_page('app/static/md/no_course_landing.md', title='Learn How to Tell Your Boss, Your Friends, and Your Family "No"')
