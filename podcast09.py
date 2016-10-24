from app.podcasts import Podcast
from app.db_config import collections
from datetime import datetime

episode_number = 17
collection = collections['pitreflections']['collection']
collection.remove({'episode_number': episode_number})
new_episode = Podcast(title="Make Some Time so You can Stay on Track",
                     episode_number=episode_number,
                     publish_date=datetime.now(),
                     url="http://traffic.libsyn.com/pitreflections/PIT_Reflections__17.mp3",
                     description = """I had a little bit of a reflection from [Anthony Gauna's Vlog](https://youtu.be/fwSaMpRbvlo) and I thought I would talk a little about why I even do reflections. 

I really believe that if you don't take some time for yourself and "meditate" you allow things to stay in your head. 

In this reflection I talk about staying on the right track and how to course correct. 

### My Takeaway for today (Click to Tweet)

- [You have to take time for yourself](http://ctt.ec/V5HNs)
- [Check you course frequently and adjust when necessary](http://ctt.ec/JF7bX)
""",
    collection=collection)
new_episode.add()
