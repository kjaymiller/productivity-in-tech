from links import (
                    Twitter,
                    Facebook,
                    ITunes,
                    Google,
                    RSS,
                    TuneIn,
                    Stitcher,
                    Overcast,
                    PocketCasts)

from models import Podcast

PITReflections = Podcast(
        title='PIT Reflections',
        collection_name='pitreflections',
        abbreviation='PITReflections',
        logo_href="http://productivityintech.com/files/images/PITReflections.png",
        summary="Daily reflections from founder of Productivity in Tech, Jay \
Miller. This podcast was created to encourage you to start thinking about what \
happened in your day and what you can learn from it.",
        links=[ITunes('https://itunes.apple.com/us/podcast/productivity-in-tech-reflections/id1161292423'),
               Google('https://play.google.com/music/listen#/ps/I5essfo5jx2xknxq4vbrmylpjl4'),
               RSS('http://productivityintech.com/static/pitreflections.rss'),
               Overcast('https://overcast.fm/itunes1161292423/productivity-in-tech-reflections')])

PITPodcast = Podcast(
        title='Productivity in Tech Podcast',
        abbreviation='PIT',
        collection_name='pitpodcast',
        logo_href='http://productivityintech.com/files/images/pitpodcast_logo_itunes.png',
        summary="Weekly podcast where I sit down and talk with people in \
tech that love productivity. Or at least love talking about it.",
        links=[ITunes('https://itunes.apple.com/us/podcast/productivity-in-tech-podcast/id1086437786?mt=2'),
               Google('https://play.google.com/music/listen#/ps/Isoopwbe6zdbev5ijenegkcpp44'),
               RSS('http://feedpress.me/pitpodcast.rss'),
               PocketCasts('http://pca.st/4f8O')])

Loosely_Connected = Podcast(
        title='Loosely Connected',
        abbreviation='Connection',
        collection_name='loosely_connected',
        logo_href='http://productivityintech.com/files/images/loosely_connected_logo.png',
        summary="Weekly Conversations between PIT Founder Jay Miller and \
Productivity Coach Lee Stetson.",
        links=[ITunes('https://itunes.apple.com/us/podcast/loosely-connected/id1214180799?mt=2'),
               Google('https://playmusic.app.goo.gl/?ibi=com.google.PlayMusic&isi=691797987&ius=googleplaymusic&link=https://play.google.com/music/m/Iesmjf7jqkuqwzlh34cbc2gly3i?'),
               RSS('http://feedpress.me/loosely_connected.rss')])



podcasts = {'pitpodcast': PITPodcast,
            'pitreflections': PITReflections,
           'loosely_connected': Loosely_Connected}
