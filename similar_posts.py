from collections import Counter

def similar_posts(entry, collection):
        posts = []
        for tag in entry.get('tags', []):
            entries = collection.find({'tags': tag})
            posts.extend([('./'+ str(x['_id']), x['title']) for x in entries])

        strip_post = filter(lambda x: x[1] != entry['title'], posts)
        return Counter(strip_post).most_common(4)

