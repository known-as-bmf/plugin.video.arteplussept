from xbmcswift2 import Plugin
import json
import urllib2

base_url = 'http://www.arte.tv'

categories = [('new',         30001),
              ('selection',   30002),
              ('most_viewed', 30003),
              ('last_chance', 30004)]
# http://www.arte.tv/papi/tvguide/videos/stream/{lang}/{id}_PLUS7-{lang}/{protocol}/{quality}.json
# lang     : F | D
# protocol : HBBTV | RTMP
# quality  : SQ (High) | EQ (Med) | HQ (Low)
video_json = base_url + '/papi/tvguide/videos/stream/{lang}/{id}_PLUS7-{lang}/{protocol}/ALL.json'
# http://www.arte.tv/papi/tvguide/videos/livestream/F/
live_json = base_url + '/papi/tvguide/videos/livestream/{lang}/'

plugin = Plugin()

language = 'fr' if plugin.get_setting('lang', int) == 0 else 'de'
quality = plugin.get_setting('quality', int)
protocol = 'HBBTV' if plugin.get_setting('protocol', int) == 0 else 'RMP4'

@plugin.route('/')
def index():
    items = [{
        'label': plugin.get_string(value),
        'path': plugin.url_for('show_' + key)
    }for key, value in categories]
    items.append({
        'label': plugin.get_string(30005),
        'path': plugin.url_for('play_live'),
        'is_playable': True
    })
    return items

@plugin.route('/new', name='show_new', options={'json_url': base_url + '/guide/{lang}/plus7.json'})
@plugin.route('/selection', name='show_selection', options={'json_url': base_url + '/guide/{lang}/plus7/selection.json'})
@plugin.route('/most_viewed', name='show_most_viewed', options={'json_url': base_url + '/guide/{lang}/plus7/plus_vues.json'})
@plugin.route('/last_chance', name='show_last_chance', options={'json_url': base_url + '/guide/{lang}/plus7/derniere_chance.json'})
def list(json_url):
    plugin.set_content('tvshows')
    data = json.loads(get_url(json_url.format(lang=language)))
    items=[{
        'label': video['title'].encode('utf-8'),
        'path': plugin.url_for('play', id=str(video['em'])),
        'thumbnail': video['image_url'],
        'is_playable': True,
        'info_type': 'video',
        'info': {
            'label': video['title'].encode('utf-8'),
            'title': video['title'].encode('utf-8'),
            'duration': str(video['duration']),
            'genre': video['video_channels'].encode('utf-8'),
            'plot': video['desc'].encode('utf-8'),
            'aired': video['airdate_long'].encode('utf-8'),
        },
        'properties': {
            'fanart_image': video['image_url'],
        },
    } for video in data['videos']]
    return plugin.finish(items)

@plugin.route('/play/<id>', name='play')
def play(id):
    return plugin.set_resolved_url(create_item(id))

@plugin.route('/live', name='play_live')
def play_live():
    fetch_url = live_json.format(lang=language[0].upper())
    data = json.loads(get_url(fetch_url))
    return plugin.play_video({
        'label': data['video']['VTI'].encode('utf-8'),
        'path': (data['video']['VSR'][0]['VUR'] + ' live=1').encode('utf-8')
    })

def create_item(id):
    fetch_url = video_json.format(id=id, lang=language[0].upper(), protocol=protocol)
    data = json.loads(get_url(fetch_url))
    try:
        url = data['video']['VSR'][quality]['VUR'].encode('utf-8')
    except:
        url = data['video']['VSR'][0]['VUR'].encode('utf-8')
    item =  {
        'label': data['video']['VTI'].encode('utf-8'),
        'path': url
    }
    return item

def get_url(url):
    req = urllib2.Request(url)
    response = urllib2.urlopen(req)
    link = response.read()
    response.close()
    return link

if __name__ == '__main__':
    plugin.run()
