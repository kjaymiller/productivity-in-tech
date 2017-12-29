from app import app, mail
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
from markdown import markdown
import requests
from blog import blog
from load_config import load_config
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
import stripe
from mailchimp_config import mailchimp_client

cfg = load_config('config.yml')
STRIPE = cfg['stripe']
stripe.api_key = STRIPE['API_KEY']

no_shownotes = "I'm sorry but shownotes have not been completed for this episode"
default_sort_direction = [('publish_date', -1)]

def filter_by_date(publish_filter_parameter={'$lt': datetime.now(pytz.utc)}):
  return {'publish_date': publish_filter_parameter}


def get_pages(collection, page, limit):
    """Creates Page Logic for Archives"""
    page_index = (page - 1) * limit
    entries = collection.find(filter_by_date(), sort=default_sort_direction)
    if not entries.count():
        return None

    start_id = entries[page_index]
    date_filter = {'$lte':start_id['publish_date']}
    return collection.find(
        filter_by_date(date_filter), sort=default_sort_direction).limit(limit)


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
    podcast = podcasts['pitpodcast']
    episode = podcast.collection.find_one(filter_by_date(), sort=default_sort_direction)
    if episode:
        episode['content'] = interval(episode['content'])
    
    blog_post = blog.collection.find_one(filter_by_date(), sort=default_sort_direction)
    if blog_post:
        blog_post['content'] = interval(blog_post['content'])
    return render_template(
        'index.html',
        podcast = podcast,
        episode = episode,
        blog_post = blog_post,
        )
  
@app.route('/pitpodcast/latest')
@app.route('/pitpodcast/last')
@app.route('/pitpodcast/<int:episode_number>')
@app.route('/pitpodcast/<id>')
@app.route('/podcast/latest')
@app.route('/podcast/last')
@app.route('/podcast/<int:episode_number>')
@app.route('/podcast/<id>')
def play(id=None, episode_number=None):
    podcast = podcasts['pitpodcast']
    collection = podcast.collection
    last_episode = last(collection)

    if episode_number:
        episode = collection.find_one({'episode_number': episode_number})
    elif id:
        episode = collection.find_one({'_id': ObjectId(id)})
    else:
        episode = last_episode

    shownotes = Markup(markdown(episode.get('content', no_shownotes)))
    return render_template(
        'play.html',
        episode=episode,
        shownotes=shownotes,
        podcast=podcast,
        header=True,
        id=episode['_id'],
        other_posts=similar_posts(episode, collection),
        )


@app.route('/pitpodcast/ep/<int:episode_number>')
@app.route('/podcast/ep/<int:episode_number>')
def episode_by_episode_number(podcast, episode_number):
    podcast = get_podcast(podcast)
    collection = podcast.collection
    episodes = collection.find(filter_by_date(), sort=[('publish_date', 1)])
    max_episode_number = episodes.count()
    
    if episode_number <= max_episode_number:
        episode = episodes[episode_number - 1]
    
    else:
        episode = episodes[max_episode_number - 1]

    shownotes = Markup(markdown(episode.get('content', no_shownotes)))
    return render_template(
        'play.html',
        episode=episode,
        shownotes=shownotes,
        podcast=podcast,
        header=True,
        other_posts=similar_posts(episode, collection),
        )


@app.route('/pitmaster')
@app.route('/podcast')
@app.route('/podcast/list')
@app.route('/podcast/archive')
@app.route('/pitpodcast')
@app.route('/pitpodcast/list')
@app.route('/pitpodcast/archive')
def podcast_archive(limit=10):
    podcast = podcasts['pitpodcast']
    page = int(request.args.get('page', 1))
    collection = podcast.collection
    episodes = get_pages(collection, page, limit)
    max_page = collection.find(filter_by_date()).count()/limit
    return render_template(
        'podcast_archive.html', 
        podcast=podcast,
        episodes=episodes, page=page, 
        max_page=max_page, header=True,
        )


@app.route('/blog')
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
@app.route('/mentorship')
def coaching():
    return load_markdown_page(
        page='app/static/md/coaching.md', 
        title="Let Me Help You Get Productive",
        )


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

@app.route('/vault')
def vault():
    if 'logged_in' in session:
        return render_template('vault.html')
    return render_template(
        '/login.html', 
        message='Before you can access the vault, You will need to login.',
        redirect= 'vault')


@app.route('/courses/say-no', methods=['GET', 'POST'])
def say_no():
    return redirect(url_for('index'))
