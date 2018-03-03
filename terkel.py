import calendar

import requests
import feedgen.feed
import dateutil
import pytz

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
fg.podcast.itunes_author('Studs Terkel')
fg.description('The WFMT Radio Network, along with the Studs Terkel Center for Oral History of the Chicago History Museum and many other committed partners, are working toward turning this site into the first-ever, comprehensive online Studs Terkel Radio Archive.')

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
        created_datetime = dateutil.parser.parse(entry['created'][0])
        try:
            original_broadcast = dateutil.parser.parse(entry['archival_broadcast_date'][0],
                                                       default=created_datetime)
        except (KeyError, ValueError):
            try:
                original_broadcast = dateutil.parser.parse(entry['wfmt_date_broadcast'][0],
                                                           default=created_datetime)
            except (calendar.IllegalMonthError, KeyError):
                original_broadcast = created_datetime
            
        original_broadcast = pytz.utc.localize(original_broadcast)
        fe.published(original_broadcast)
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

