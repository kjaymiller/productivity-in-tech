from app import app
from app.mongo import (get_episode, podcast_coll)
from app.podcasts import next_episode_number
from app import site_config
from markdown import markdown

from app.forms import add_podcast
from flask import render_template, redirect, url_for, request, Markup


@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html',
                           config=site_config,)


@app.route('/podcast/<ep_number>')
def play(ep_number):
    episode = get_episode(int(ep_number))
    show_notes = Markup(markdown(episode['show_notes']))
    return render_template('play.html', episode=episode, show_notes=show_notes)


@app.route('/podcast/add', methods=['GET', 'POST'])
def add_episode():
    form = add_podcast()
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
            'episode_number': next_episode_number(podcast_coll),
            'media_url': media_url}

        podcast_coll.insert_one(episode)

        return redirect(url_for('play',
                                ep_number=episode['episode_number']))

    elif request.method == 'POST':
        return 'ERROR'

    return render_template('newep.html', form=form)
