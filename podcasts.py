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

PITPodcast = Podcast(
        title='Productivity in Tech Podcast',
        abbreviation='PIT',
        collection_name='pitpodcast',
        logo_small='http://productivityintech.com/files/images/pitpodcast_logo_2_500.png',
        logo_href='http://productivityintech.com/files/images/pitpodcast_logo_2.png',
        summary="Weekly podcast where I sit down and talk with people in \
tech that love productivity. Or at least love talking about it.",
        links=[ITunes('https://itunes.apple.com/us/podcast/productivity-in-tech-podcast/id1086437786?mt=2'),
               Google('https://play.google.com/music/listen#/ps/Isoopwbe6zdbev5ijenegkcpp44'),
               Overcast('https://overcast.fm/itunes1086437786/productivity-in-tech-podcast'),
               PocketCasts('https://play.pocketcasts.com/web/podcasts/index#/podcasts/show/28cf7bb0-ba97-0133-2e57-6dc413d6d41d'),
               RSS('http://feedpress.me/pitpodcast.rss')])

podcasts = {'pitpodcast': PITPodcast}
