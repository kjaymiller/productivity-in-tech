from models import Link


class Twitter(Link):
    name = 'Twitter'
    image_path = '/static/images/Twitter-Icon.png'
    def __init__(self, username):
        self.url = 'http://twitter.com/' + username
        self.username = '@' + username


class Facebook(Link):
    name = 'Facebook'
    image_path = '/static/images/FB-f-Logo__blue_58.png'


class ITunes(Link):
    name = 'iTunes'
    image_path = '/static/images/Get_it_on_iTunes_Badge_US_1114.svg'


class Google(Link):
    name = 'Google'
    image_path = '/static/images/play_en_badge_web_generic.png'


class RSS(Link):
    name = 'RSS'
    image_path = '/static/images/rss.png'


class TuneIn(Link):
    name = 'tunein'
    image_path = '/static/images/rss.png'


class Stitcher(Link):
    name = 'Stitcher'


class Overcast(Link):
    name = 'Overcast'
    image_path = '/static/images/overcastfm.svg'


class PocketCasts(Link):
    name = 'PocketCasts'
    image_path = '/static/images/pocketcasts_logo.png'
