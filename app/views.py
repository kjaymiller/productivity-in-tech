from app import app
from blog import blog
from bson.objectid import ObjectId
from flask import (render_template,
                   redirect,
                   url_for,
                   Markup,
                   make_response,
                   request,
                   jsonify,
                   abort)
from markdown import markdown
from models import (last,
                    total_pages,
                    podcast_page,
                    latest_episode,
                    latest_post)
from datetime import datetime
from podcasts import podcasts

@app.route('/podcasts')
@app.route('/subscribe')
def list_podcasts():
    return render_template('podcasts.html', header=True)

@app.route('/fots/<oid>')
def get_image(oid):
    friend = friends_coll.find_one({'_id': ObjectId(oid)})
    photo = friend['photo']
    response = make_response(photo)
    response.mimetype = 'image/png'
    return response

@app.route('/mobile')
def mobile():
    return render_template('mobile.html')


@app.route('/')
@app.route('/index')
def index():
    # latest = []
    # latest.append(.podcast.find({}, sort=[(publish_date, -1)])[0])
    #   latest_episode = max(latest)
    return render_template('index.html', latest_episode=latest_episode)


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
    return render_template('blog.html', blog=posts, header=True)

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


@app.route('/friends')
def friends_of_show():
    friends = friends_coll.find()
    return render_template('friends.html', friends=friends, header=True)


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


@app.route('/coc')
def conduct():
    with open('app/static/coc.md') as f:
        body = Markup(markdown(f.read()))
    return render_template('coc.html', body=body)
