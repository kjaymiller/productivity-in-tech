from flask.ext.wtf import Form
from wtforms import (StringField, TextAreaField, validators)


class add_podcast_episode(Form):
    title = StringField('title', [validators.InputRequired()])
    guest_name = StringField('guest name', [validators.Optional()])
    guest_twitter = StringField('guest_twitter', [validators.Optional()])
    guest_site = StringField('guest site',
                             [validators.Optional(),
                              validators.URL('URL Required')])
    show_notes = TextAreaField('show_notes', [validators.InputRequired()])
    media_url = StringField('media url', [validators.URL('URL Required')])


class add_blog_post(Form):
    title = StringField('title', [validators.InputRequired()])
    author_username = StringField('author')
    body = TextAreaField('show_notes', [validators.InputRequired()])
