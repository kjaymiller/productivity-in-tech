from flask import (
    Blueprint,
    render_template,
    request,
    Markup,
    )
from bson.objectid import ObjectId
from podcasts import podcasts
from mongo import (
    get_pages,
    filter_by_date,
    )
from models import (
    last,
    podcast_page,
    latest_episode,
    latest_post,
    )
import markdown
podcast_mod = Blueprint(
    'podcast',
    __name__, 
    template_folder='templates',
    )

no_shownotes = "I'm sorry but shownotes have not been completed for this episode"

@podcast_mod.route('/list')
@podcast_mod.route('/archive')
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


@podcast_mod.route('/podcast/latest')
@podcast_mod.route('/podcast/last')
def play_last():
    podcast = podcasts['pitpodcast']
    collection = podcast.collection

    episode = last(collection)
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


@podcast_mod.route('/podcast/<id>')
def play(id):
    podcast = podcasts['pitpodcast']
    collection = podcast.collection

    episode = collection.find_one({'_id': ObjectId(id)})
    shownotes = Markup(markdown(episode.get('content', no_shownotes)))
    return render_template(
        'play.html',
        episode=episode,
        shownotes=shownotes,
        podcast=podcast,
        heaer=True,
        id=episode['_id'],
        other_posts=similar_posts(episode, collection),
        )


@podcast_mod.route('/podcast/<int:episode_number>')
@podcast_mod.route('/pitpodcast/ep/<int:episode_number>')
@podcast_mod.route('/podcast/ep/<int:episode_number>')
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
