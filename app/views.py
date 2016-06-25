from app import app
from pymongo import ASCENDING as ASC
from app.mongo import podcast_coll 
from app import site_config
from app.forms import add_podcast_episode
from flask import render_template, redirect, url_for, request


@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html',
                           config=site_config,)


@app.route('/podcast/<episode_number>')
def play(episode_number):
    episode = podcast_coll.find_one({'episode_number': int(episode_number)})
    return render_template('play.html', episode=episode)


@app.route('/podcast/archive')
def podcast_archive():
    episodes = [x for x in podcast_coll.find(sort=[('episode_number', ASC)])]
    return render_template('podcast_archive.html', episodes=episodes)


@app.route('/podcast/add', methods=['GET', 'POST'])
def add_episode():
    form = add_podcast_episode()
    if form.validate_on_submit():
        title = form.title.data
        guest = {'name': form.guest_name.data,
                 'website': form.guest_site.data,
                 'twitter': form.guest_twitter.data}
        show_notes = form.show_notes.data
        media_url = form.media_url.data

        episode = {
            'title': title,
            'guest': guest,
            'show_notes': show_notes,
            'media_url': media_url}

        podcast_coll.insert_one(episode)

        return redirect(url_for('play',
                                ep_number=episode['episode_number']))

    elif request.method == 'POST':
        return 'ERROR'

    return render_template('newep.html', form=form)


@app.route('/admin', methods=['GET', 'POST'])
def admin():
    return 'foo'


@app.route('/admin/login')
def admin_login():
    return ''
