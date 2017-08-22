import json
import stripe
import requests
import pytz
from app import app
from blog import blog
from config import STRIPE_API_KEY, SLACK_TOKEN
from bson.objectid import ObjectId
from flask import (render_template,
                   redirect,
                   url_for,
                   Markup,
                   make_response,
                   request,
                   jsonify,
                   abort)
from links import RSS, Google, ITunes, Overcast, PocketCasts
from markdown import markdown
from models import (last,
                    podcast_page,
                    latest_episode,
                    latest_post)
from slack import Goal
from titlecase import titlecase
from datetime import datetime
from podcasts import podcasts
from urllib.error import HTTPError
from urllib.request import urlopen

stripe.api_key = STRIPE_API_KEY

def load_markdown_page(page):
    with open(page) as f:
        title = page.split('/')[-1][:-3] # [-3 removes .md extension]
        body = Markup(markdown(f.read()))
    return render_template('markdown_page.html', body=body, title=titlecase(title))

@app.route('/podcasts')
def list_podcasts():
    return render_template('podcasts.html', podcasts=podcasts, header=True)


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
        post_preview = Markup(markdown(recent_posts['content'][:140]))

    return render_template('index.html',
                            latest_podcast=latest_podcast,
                            posts=recent_posts,
                            post_preview=post_preview)


@app.route('/<podcast>/latest')
@app.route('/<podcast>/last')
@app.route('/<podcast>/<int:episode_number>')
@app.route('/<podcast>/<id>')
def play(podcast, id=None, episode_number=None):
    podcast = podcasts[podcast.lower()]
    collection = podcast.collection
    last_episode = last(collection)
    if episode_number:
        episode = collection.find_one({'episode_number': episode_number})
    elif id:
        episode = collection.find_one({'_id': ObjectId(id)})
    else:
        episode = last_episode

    if 'content' in episode.keys():
        shownotes = Markup(markdown(episode['content']))
    else:
        shownotes = "I'm sorry but shownotes have not been completed for this episode"

    return render_template('play.html',
                           episode=episode,
                           shownotes=shownotes,
                           last=last_episode,
                           podcast=podcast,
                           header=True)

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
    friendly_lookup = blog.collection.find_one({'friendly': lookup})
    id_lookup = blog.collection.find_one({'_id':ObjectId(lookup)})
    if friendly_lookup:
        entry = friendly_lookup
    else:
        entry = id_lookup
    content = Markup(markdown(entry['content'])) # content is stored in html
    date_format = '%a, %d %b %Y %H:%M:%S %z'
    publish_date = datetime.strftime(entry['publish_date'], date_format)
    if 'quote' in entry.keys():
        return render_template('comment.html',
                title = titlecase(entry['title']),
                publish_date = publish_date,
                article_url = entry['url'],
                article_title = entry['article-title'],
                comment = Markup(Markdown(entry['comment'])),
                quote = entry['quote'])
    else:
        return render_template('post.html',
                entry=entry,
                title=titlecase(entry['title']),
                content=content,
                publish_date = publish_date,
                tag_length = len(entry['tags']),
                author = entry['author'],
                header=True)

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
    return load_markdown_page('app/static/md/coaching.md')
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

@app.route('/api/podcast/latest', methods=['POST'])
def latest_episode():
    collection = podcasts['pitpodcast'].collection
    latest_episode = collection.find({}, sort=[('publish_date', -1)])[0]
    return '*Latest Episode*🎙️:\n<https://productivityintech.com/pitpodcast/{}|{}>'.format(latest_episode['_id'], titlecase(latest_episode['title']))


@app.route('/api/slack/challenge', methods=['POST'])
def slack_connect():
    data = request.json
    challenge = {'challenge':data['challenge']}
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
    return load_markdown_page('app/static/md/Code of Conduct.md')

@app.route('/vision')
@app.route('/goals')
def vision_goals():
    return load_markdown_page('app/static/md/Vision and Goals.md')

@app.route('/subscribe')
@app.route('/support')
@app.route('/premium')
@app.route('/join')
def subscribe():
    sale_left = len(stripe.Customer.list()['data'])
    return render_template('subscribe.html', sale_left=sale_left)

@app.route('/payment/<plan>', methods=['POST'])
def payment_successful(plan):
    email = request.form['stripeEmail']
    customer = stripe.Customer.create(
        email=email,
        source=request.form['stripeToken']
        )
    charge = stripe.Subscription.create(
        customer=customer.id,
        plan=plan)
    requests.post('https://slack.com/api/users.admin.invite?token={}&email={}&resend=true'.format(SLACK_TOKEN, email))
    return render_template('payment_complete.html')
