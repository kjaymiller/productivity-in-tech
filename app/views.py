from app import app
from app.mongo import (get_episode, podcast_coll, blog_coll)
from app.podcasts import next_episode_number
from app.blog import get_url_title
from app import site_config
from datetime import datetime
from markdown import markdown

from app.forms import add_podcast_episode, add_blog_post
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
            'episode_number': next_episode_number(podcast_coll),
            'media_url': media_url}

        podcast_coll.insert_one(episode)

        return redirect(url_for('play',
                                ep_number=episode['episode_number']))

    elif request.method == 'POST':
        return 'ERROR'

    return render_template('newep.html', form=form)


@app.route('/blog')
def blog():
    last_5 = blog_coll.find().sort([('published_date', 1)]).limit(5)
    return render_template('blog.html', posts=last_5)


@app.route('/blog/add', methods=['GET', 'POST'])
def blog_new():
    form = add_blog_post()

    if form.validate_on_submit():
        title = form.title.data
        url_title = get_url_title(title)
        author = form.author_username.data
        body = form.body.data
        post = {
            'title': title,
            'title_url': url_title,
            'author': author,
            'body': body,
            'published_date': datetime.utcnow()
        }

        blog_coll.insert_one({'post': post})
        return redirect(url_for('preview_blog_post', title=url_title))

    return render_template('new_blog_post.html', form=form)


@app.route('/blog/<title>/preview', methods=['GET', 'POST'])
def preview_blog_post(title):
    post = blog_coll.find_one({'post.title_url': title})['post']
    body = Markup(markdown(post['body']))
    return render_template('preview_blog_post.html',
                           post=post,
                           body=body)


@app.route('/admin', methods=['GET', 'POST'])
def admin():
    return 'foo'


@app.route('/admin/login')
def admin_login():
    return ''


@app. route('/admin/dashboard')
def admin_dashboard():
    return ''
