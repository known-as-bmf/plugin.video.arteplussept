from xbmcswift2 import Plugin
from xbmcswift2 import actions
import SimpleDownloader as downloader
import json
import urllib2

base_url = 'http://www.arte.tv'

categories = [('new', 30001),
              ('selection', 30002),
              ('most_viewed', 30003),
              ('last_chance', 30004)]

# http://www.arte.tv/papi/tvguide/videos/stream/{lang}/{id}_PLUS7-{lang}/{protocol}/{quality}.json
# lang     : F | D
# protocol : HBBTV | RTMP
# quality  : SQ (High) | EQ (Med) | HQ (Low)
video_json = base_url + '/papi/tvguide/videos/stream/{lang}/{id}_PLUS7-{lang}/{protocol}/ALL.json'

# http://www.arte.tv/papi/tvguide/videos/livestream/{lang}/
# lang : F | D
live_json = base_url + '/papi/tvguide/videos/livestream/{lang}/'

# http://www.arte.tv/guide/{lang}/plus7/par_dates.json?value={date}
# lang : fr | de
# date : date sous la forme yyy-mm-jj

# http://www.arte.tv/guide/{lang}/plus7/par_themes.json?value={genre}
# lang  : fr | de
# genre : trigramme du genre (ACT DOC DEC EUR GEO SOC JUN AUT CIN ART CUL ENV)

# http://www.arte.tv/guide/{lang}/plus7/par_emissions.json?value={emission}
# lang     : fr | de
# emission : trigramme de l'emission (VMI TSG AJT JTE COU FUM KAR DCA MTR PNB PHI SUA TRA VOX XEN YOU

plugin = Plugin()
downloader = downloader.SimpleDownloader()

language = 'fr' if plugin.get_setting('lang', int) == 0 else 'de'
language_live = 'f' if plugin.get_setting('lang', int) == 0 else 'd'
quality = plugin.get_setting('quality', int)
protocol = 'HBBTV' if plugin.get_setting('protocol', int) == 0 else 'RMP4'

download_dir = plugin.get_setting('folder', str)


@plugin.route('/')
def index():
    items = [{
        'label': plugin.get_string(value),
        'path': plugin.url_for('show_' + key)
    } for key, value in categories]
    items.append({
        'label': plugin.get_string(30005),
        'path': plugin.url_for('play_live'),
        'is_playable': True
    })
    return items


@plugin.route('/new', name='show_new',
              options={'json_url': base_url + '/guide/{lang}/plus7.json'})
@plugin.route('/selection', name='show_selection',
              options={'json_url': base_url + '/guide/{lang}/plus7/selection.json'})
@plugin.route('/most_viewed', name='show_most_viewed',
              options={'json_url': base_url + '/guide/{lang}/plus7/plus_vues.json'})
@plugin.route('/last_chance', name='show_last_chance',
              options={'json_url': base_url + '/guide/{lang}/plus7/derniere_chance.json'})
def list(json_url):
    plugin.set_content('tvshows')
    data = json.loads(get_url(json_url.format(lang=language)))
    items = [{
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
            'plot': video['desc'].encode('utf-8') if video['desc'] is not None else '',
            'aired': video['airdate_long'].encode('utf-8'),
        },
        'properties': {
            'fanart_image': video['image_url'],
        },
        'context_menu': [
            (plugin.get_string(30021), actions.background(plugin.url_for('download', id=str(video['em'])))),
        ],
    } for video in data['videos']]
    return plugin.finish(items)


@plugin.route('/play/<id>', name='play')
def play(id):
    return plugin.set_resolved_url(create_item(id))


@plugin.route('/download/<id>', name='download')
def download_file(id):
    data = load_json(id)
    params = {
        'url': data['video']['VSR'][quality]['VUR'].encode('utf-8'),
        'download_path': download_dir,
        'Title': data['video']['VTI'].encode('utf-8')
    }
    filename = id + data['video']['VST']['VNA'] + '.mp4'
    downloader.download(filename.encode('utf-8'), params)


@plugin.route('/live', name='play_live')
def play_live():
    fetch_url = live_json.format(lang=language_live[0].upper())
    data = json.loads(get_url(fetch_url))
    url = data['video']['VSR'][0]['VUR'].encode('utf-8')
    return plugin.play_video({
        'label': data['video']['VTI'].encode('utf-8'),
        'path': (url + ' live=1').encode('utf-8')
    })

quality_map = { 0: 'SQ', 1: 'EQ', 2: 'HQ' }
def create_item(id):
    data = load_json(id)
    url = None
    for version in data['video']['VSR']:
        if version['VQU'] == quality_map[quality]:
            url = version['VUR'].encode('utf-8')
            break
    if not url:
        url = data['video']['VSR'][0]['VUR'].encode('utf-8')
    item = {
        'label': data['video']['VTI'].encode('utf-8'),
        'path': url
    }
    return item


def load_json(id):
    fetch_url = video_json.format(id=id, lang=language[0].upper(), protocol=protocol)
    return json.loads(get_url(fetch_url))


def get_url(url):
    req = urllib2.Request(url)
    response = urllib2.urlopen(req)
    link = response.read()
    response.close()
    return link


if __name__ == '__main__':
    plugin.run()
