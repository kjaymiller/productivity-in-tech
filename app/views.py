import json
import stripe
import requests
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
                    total_pages,
                    podcast_page,
                    latest_episode,
                    latest_post)
from datetime import datetime
from podcasts import podcasts
from urllib.error import HTTPError
from urllib.request import urlopen


def load_markdown_page(page):
    with open(page) as f:
        title = page.split('/')[-1][:-3] # [-3 removes .md extension]
        body = Markup(markdown(f.read()))
    return render_template('markdown_page.html', body=body, title=title.title())


@app.route('/podcasts')
def list_podcasts():
    return render_template('podcasts.html', podcasts=podcasts, header=True)


@app.route('/')
@app.route('/index')
def index():
    latest_podcast = []
    for podcast in podcasts:
        collection = podcasts[podcast].collection
        recent_episode = (collection.find({'published': True}, sort=[('publish_date', -1)])[0])
        recent_episode['podcast'] = podcasts[podcast]
        recent_episode['links'] = podcasts[podcast].links
        latest_podcast.append(recent_episode)

        collection = blog.collection
        recent_posts = (collection.find({}, sort=[('publish_date', -1)])[0:4])

    return render_template('index.html',
                            latest_podcast=latest_podcast,
                            posts=recent_posts)


@app.route('/<podcast>/latest')
@app.route('/<podcast>/last')
@app.route('/<podcast>/<int:episode_number>')
def play(podcast, episode_number=0):
    podcast = podcasts[podcast.lower()]
    collection = podcast.collection
    last_episode = last(collection)

    if episode_number > last_episode['episode_number'] or not episode_number:
        episode_number = last_episode

    episode = collection.find_one({'episode_number': episode_number})

    if not episode:
        episode = collection.find_one({'published': True},limit=1,sort=[('episode_number', -1)])

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
@app.route('/<podcast>/list/<int:page>')
#  @app.route('/<podcast>/archive/<int:page>')
def podcast_archive(podcast, page=0):
    podcast = podcasts[podcast.lower()]
    collection = podcast.collection
    nav = total_pages(page=page, collection=collection)
    episodes = podcast_page(page=page, collection=collection)
    return render_template('podcast_archive.html', nav=nav, podcast=podcast,
                            episodes=episodes, header=True)

@app.route('/blog')
def blog_list():
    posts = blog.collection.find({}, sort=[('publish_date', -1)])
    return render_template('blog.html', blog=blog, posts=posts, header=True)

@app.route('/blog/<lookup>')
def post(lookup=None):
    friendly_lookup = blog.collection.find_one({'friendly': lookup})
    id_lookup = blog.collection.find_one({'_id':ObjectId(lookup)})
    if friendly_lookup:
        entry = friendly_lookup
    elif id_lookup:
        entry = id_lookup
    else:
        return render_template('blog.html', blog=Blog.collection.find())
    content = Markup(markdown(entry['content'])) # content is stored in html
    date_format = '%a, %d %b %Y %H:%M:%S %z'
    publish_date = datetime.strftime(entry['publish_date'], date_format)
    return render_template(
            'post.html',
            entry=entry,
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
            title=title,
            no_episode=no_episode)

@app.route('/community')
@app.route('/join')
def join():
    return render_template('join.html', header=True)


@app.route('/feedback')
def feedback():
    return render_template('feedback.html')


@app.route('/support')
def support():
    return render_template('support.html', header=True)


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


#get the current podcast episode count
@app.route('/api/web/<podcast>/length')
def count_podcast_length(podcast):
    podcast = collections[podcast.lower()]
    collection = podcast.collection
    return str(last(collection))


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
def subscribe():
    return render_template('subscribe.html')

@app.route('/payment/<plan>', methods=['POST'])
def payment_successful():
    stripe.api_key = STRIPE_API_KEY
    #Amount in cents
    amount = 1000
    email = request.form['stripeEmail']
    customer = stripe.Customer.create(
        email=email,
        source=request.form['stripeToken']
        )
    charge = stripe.Subscription.create(
        customer=customer.id,
        plan=plan
        )
    requests.post('https://slack.com/api/users.admin.invite?token={}&email={}&resend=true'.format(SLACK_TOKEN, email))
    return render_template('payment_complete.html')
