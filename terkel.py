import requests
import feedgen.feed

def all_entries(base_url, increment):
    start = 0
    while True:

        query = base_url.format(start, increment)

        entries = requests.get(query).json()['file']['files']

        if entries:
            yield from entries
        else:
            break

        start += increment
        print(start)

fg = feedgen.feed.FeedGenerator()
fg.load_extension('podcast')
fg.link(href='http://example.com', rel='alternate' )
fg.title('The Studs Terkel Radio Archive')
fg.author( {'name':'John Doe','email':'john@example.de'} )
fg.description('foo')

query = 'https://studsterkel.digitalrelab.com/lwm/ajax.php?operation=text-search&txt=&limit={},{}&sort=created_DESC'

seen = set()

for entry in all_entries(query, 25):
    duration = int(float(entry['playtime_seconds']))
    if duration > (60 * 15):
        
        url = entry['fav_url']
        title = entry['title']
        if not url or not title or url in seen:
            continue

        seen.add(url)
        fe = fg.add_entry()
        fe.id(url)
        fe.title(entry['title'])
        fe.enclosure(url, entry['size'], 'audio/mpeg')
        fe.podcast.itunes_duration(duration)
        fe.updated(entry['modified'])
        fe.published(entry['created'])
        try:
            fe.rss_entry()
        except:
            import pdb
            pdb.set_trace()

try:
    fg.rss_str(pretty=True)
except:
    import pdb
    pdb.set_trace()
fg.rss_file('podcast.xml')    

