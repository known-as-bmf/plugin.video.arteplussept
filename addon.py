
# coding=utf-8
# -*- coding: utf-8 -*-
#
# plugin.video.arteplussept, Kodi add-on to watch videos from http://www.arte.tv/guide/fr/plus7/
# Copyright (C) 2015  known-as-bmf
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.
#

from xbmcswift2 import Plugin
from xbmcswift2 import actions
import requests
import os
import urllib2
import time
import datetime


plugin = Plugin()

base_url = 'http://www.arte.tv'

# http://www.arte.tv/papi/tvguide/videos/stream/{lang}/{id}_PLUS7-{lang}/{protocol}/{quality}.json
# lang     : F | D
# protocol : HBBTV | RTMP
# quality  : SQ (High) | EQ (Med) | HQ (Low)
video_json = base_url + '/papi/tvguide/videos/stream/player/{lang}/{id}_PLUS7-{lang}/{protocol}/ALL.json'
video_json = 'https://api.arte.tv/api/player/v1/config/{lang}/{id}'
daily_json = 'https://www.arte.tv/hbbtvv2/services/web/index.php/OPA/v3/programs/{date}/de'
# http://www.arte.tv/papi/tvguide/videos/livestream/{lang}/
# lang : F | D
live_json = base_url + '/papi/tvguide/videos/livestream/{lang}/'

# http://www.arte.tv/papi/tvguide/videos/plus7/program/{lang}/{detailLevel}/{category}/{cluster}/{recommended}/{sort}/{limit}/{offset}/DE_FR.json
# lang : F | D
# detailLevel : L2 | L3 (the higher the most verbose)
# category : categorie (HIS... see below)
# cluster : emission (VMI... see below)
# recommended : 1 | -1
# sort : AIRDATE_DESC | AIRDATE_ASC | ALPHA | VIEWS | LAST_CHANCE
# limit : n of results
# offset : starts at 1
#
# cluster : emission
# 28 Minutes                        VMI
# 360° GEO                          TSG
# ARTE Journal                      AJT
# ARTE Junior                       JUN
# ARTE Reportage                    JTE
# Au cœur de la nuit                ACN
# Cinéma sur ARTE                   FIL
# Court-circuit                     COU
# Cuisines des terroirs             CUI
# Futuremag                         FUM
# Karambolage                       KAR
# Le Dessous des cartes             DCA
# Maestro                           MAE
# Metropolis                        MTR
# Personne ne bouge !               PNB
# Philosophie                       PHI
# Square                            SUA
# Tracks                            TRA
# Vox Pop                           VOX
# X:enius                           XEN
# Yourope                           YOU
#
# category : categories
# Actu & société                    ACT
# Séries & fiction                  FIC
# Cinéma                            CIN
# Arts & spectacles classiques      ART
# Culture pop                       CUL
# Découverte                        DEC
# Histoire                          HIS
# Junior                            JUN
listing_json = base_url + '/papi/tvguide/videos/plus7/program/{lang}/L2/{category}/{cluster}/{highlight}/{sort}/{limit}/{offset}/DE_FR/{date}.json'


def get_menu_items():
    return [(plugin.url_for('listing'),                                   30001), # new http://www.arte.tv/papi/tvguide/videos/plus7/program/F/L2/ALL/ALL/-1/AIRDATE_DESC/0/0/DE_FR.json
            (plugin.url_for('listing', highlight='1', limit='6'),         30002), # selection http://www.arte.tv/papi/tvguide/videos/plus7/program/F/L2/ALL/ALL/1/AIRDATE_DESC/6/0/DE_FR.json
            (plugin.url_for('listing', sort='VIEWS', limit='20'),         30003), # most_viewed http://www.arte.tv/papi/tvguide/videos/plus7/program/F/L2/ALL/ALL/-1/VIEWS/0/0/DE_FR.json
            (plugin.url_for('listing', sort='LAST_CHANCE', limit='20'),   30004), # last chance http://www.arte.tv/papi/tvguide/videos/plus7/program/F/L2/ALL/ALL/-1/LAST_CHANCE/0/0/DE_FR.json
            (plugin.url_for('dates'),                                     30005), # dates http://www.arte.tv/papi/tvguide/videos/plus7/program/F/L2/ALL/ALL/-1/LAST_CHANCE/0/0/DE_FR.json
            (plugin.url_for('categories'),                                30006)] # categories http://www.arte.tv/papi/tvguide/videos/plus7/program/F/L2/XXX/ALL/-1/AIRDATE_DESC/0/0/DE_FR.json


def get_categories():
    return [('actu-societe', 3000501),
            ('series-fiction', 3000502),
            ('cinema', 3000503),
            ('arts-spectacles-classiques', 3000504),
            ('culture-pop', 3000505),
            ('decouverte', 3000506),
            ('histoire', 3000507),
            ('junior', 3000508)]


def get_dates():
    today = datetime.date.today()
    one_day = datetime.timedelta(days=1)

    dates = []
    dates.append((str(today), plugin.get_string(30008))) # Today
    dates.append((str(today - one_day), plugin.get_string(30009))) # Yesterday
    for i in xrange(2, 8): #TODO: find better interval
        cdate = today - (one_day * i)
        dates.append((str(cdate), '{d:%A}, {d:%d}'.format(d=cdate)))
    return dates

headers = {'user-agent': plugin.name + '/' + plugin.addon.getAddonInfo('version')}

quality_map = {0: 'SQ', 1: 'EQ', 2: 'HQ', 3: 'MQ'}

# Settings
language = 'FR' if plugin.get_setting('lang', int) == 0 else 'DE'
prefer_vost = plugin.get_setting('prefer_vost', bool)
quality = plugin.get_setting('quality', int)
protocol = 'HBBTV' if plugin.get_setting('protocol', int) == 0 else 'RMP4'
download_folder = plugin.get_setting('download_folder', str)
download_quality = plugin.get_setting('download_quality', int)


@plugin.route('/')
def index():
    items = [{
        'label': plugin.get_string(sid),
        'path': path
    } for path, sid in get_menu_items()]
    items.append({
        'label': plugin.get_string(30007),
        'path': plugin.url_for('live'),
        'is_playable': True
    })
    items.append({
        'label': 'Penis',
        'path': 'Penis',
        'is_playable': True
    })
    return items


#@plugin.route('/listing', name='listing')
def show_listing():
    plugin.set_content('tvshows')

    # very ugly workaround ahead (plugin.request.args.XXX returns an array for unknown reason)
    json_url = plugin.request.args.get('json', [listing_json])[0]

    sort = plugin.request.args.get('sort', ['AIRDATE_DESC'])[0]
    url = json_url.format(lang=language[0],
                          category=plugin.request.args.get('category', ['ALL'])[0],
                          cluster=plugin.request.args.get('cluster', ['ALL'])[0],
                          highlight=plugin.request.args.get('highlight', ['-1'])[0],
                          sort=sort,
                          limit=plugin.request.args.get('limit', ['0'])[0],
                          offset=plugin.request.args.get('offset', ['0'])[0],
                          date=plugin.request.args.get('date', [''])[0])

    data = load_json(url)

    listing_key = 'program{lang}List'.format(lang=language)

    items = []
    if not data.get(listing_key):
        return plugin.finish(items)
    for video in data[listing_key]:
        item = create_item(video.get('VDO'), {'show_airtime': plugin.request.args.get('date'),
                                              'show_deletetime': sort == 'LAST_CHANCE',
                                              'show_views': sort == 'VIEWS'})
        #item['info']['mpaa'] = video.get('mediaRating' + language[0])
        items.append(item)
    return plugin.finish(items)

def get_last7days():
    dates = [a[0] for a in get_dates()]
    progs = []
    for date in dates:
        progs += get_listing(date)
    return progs

def get_listing(date):
    #today = get_dates()[0][0]
    url = daily_json.format(date=date)
    data = load_json(url)
    return data['programs'] 
    
@plugin.route('/listing', name='listing')
#def show_listing():
def get_items():
    Programms = get_last7days()
    plugin.set_content('tvshows')
    items = []
    for prog in Programms:
        programId = prog['program']['programId']
        item = {
            'label': prog['program']['title'],
            'path': plugin.url_for('play', vid=programId),
            'thumbnail': prog['program']['imageUrl'],
            'is_playable': True,
            'info_type': 'video',
            'info': {
                'label': 'penis',
                }
            }
            
        items.append(item)
    return plugin.finish(items)

@plugin.route('/dates', name='dates')
def show_dates():
    items = [{
        'label': value,
        'path': plugin.url_for('listing', sort='AIRDATE_DESC', date=key)
    } for key, value in get_dates()]
    return plugin.finish(items)

@plugin.route('/categories', name='categories')
def show_categories():
    items = [{
        'label': plugin.get_string(value),
        'path': plugin.url_for('listing', sort='AIRDATE_DESC', category=key)
    } for key, value in get_categories()]
    return plugin.finish(items)


@plugin.route('/play/<vid>', name='play')
def play(vid):
    return plugin.set_resolved_url(create_video(vid))


@plugin.route('/enqueue/<vid>', name='enqueue')
def enqueue(vid):
    plugin.add_to_playlist([create_video(vid)])


@plugin.route('/download/<vid>', name='download')
def download_file(vid):
    if download_folder:
        video = create_video(vid, True)
        filename = vid + '_' + video['label'] + os.extsep + 'mp4'
        block_sz = 8192
        f = open(os.path.join(download_folder, filename), 'wb')
        u = urllib2.urlopen(video['path'])

        plugin.notify(filename, plugin.get_string(30010))
        while True:
            buff = u.read(block_sz)
            if not buff:
                break
            f.write(buff)
        f.close()
        plugin.notify(filename, plugin.get_string(30011))
    else:
        plugin.notify(plugin.get_string(30013), plugin.get_string(30012))


@plugin.route('/live', name='live')
def play_live():
    data = load_json(live_json.format(lang=language[0].upper()))
    url = data['video']['VSR'][0]['VUR']
    return plugin.set_resolved_url(url)#{
    #    'label': data['video']['VTI'],
    #    #'path': (url + ' live=1')
    #    'path': url
    #})


def create_item(data, options=None):
    options = options or {}


    airdate = parse_date(data.get('VDA')[:-6]) if data.get('VDA') else None

    label = ''
    # prefixes
    if options.get('show_airtime'):
            label += '[COLOR fffa481c]{d.hour:02}:{d.minute:02}[/COLOR] '.format(d=airdate)
    if options.get('show_deletetime'):
        if data.get('VRU'): # deletion found
            deletiondate = parse_date(data.get('VRU')[:-6])
            label += '[COLOR ffff0000]{d:%a} {d:%d} {d.hour:02}:{d.minute:02}[/COLOR] '.format(d=deletiondate)
    if options.get('show_views'):
        label += '[COLOR ff00aae3]{v:>6}[/COLOR] '.format(v=parse_views(data.get('VVI')))

    label += '[B]{title}[/B]'.format(title=data.get('VTI').encode('utf8'))

    # suffixes
    if data.get('VSU'):
        label += ' - {subtitle}'.format(subtitle=data.get('VSU').encode('utf8'))

    item = {
        'label': label,
        'path': plugin.url_for('play', vid=str(data.get('VPI'))),
        'thumbnail': data.get('VTU').get('IUR'),
        'is_playable': True,
        'info_type': 'video',
        'info': {
            'label': data.get('VTI'),
            'title': data.get('VTI'),
            'duration': str(data.get('videoDurationSeconds')),
            'genre': data.get('VCG'),
            'plot': data.get('VDE'),
            'plotoutline': data.get('V7T'),
            'year': data.get('productionYear'),
            'director': data.get('PPD'),
            'aired': str(airdate)
        },
        'properties': {
            'fanart_image': data.get('VTU').get('IUR'),
        },
        'context_menu': [
            (plugin.get_string(30021), actions.background(plugin.url_for('download', vid=str(data.get('VPI'))))),
            (plugin.get_string(30020), actions.background(plugin.url_for('enqueue', vid=str(data.get('VPI')))))
        ],
    }
    return item

def create_video(vid, downloading=False):
    chosen_protocol = protocol if not downloading else 'HBBTV'
    chosen_quality = quality if not downloading else download_quality

    #data = load_json(video_json.format(id=vid, lang=language[0].upper(), protocol=chosen_protocol))
    data = load_json(video_json.format(id=vid, lang=language.lower()))
    filtered = []
    video = None

    # we try every quality (starting from the preferred one)
    # if it is not found, try every other from highest to lowest
    for q in [quality_map[chosen_quality]] + [i for i in ['SQ', 'EQ', 'HQ', 'MQ'] if i is not quality_map[chosen_quality]]:
        filtered = [item for item in data['videoJsonPlayer']['VSR'].values() if match2(item,q,language)]
        # here len(filtered) sould be 1
        if len(filtered) == 1:
            video = filtered[0]
            break
    return {
        'label': data['videoJsonPlayer']['VST']['VNA'] if downloading else None, #data['videoJsonPlayer']['VTI'],
        'path': video['url'],
        'thumbnail': data['videoJsonPlayer']['VTU']['IUR']
    }

def match2(item, quality, lan):
    return (item['quality'] == quality) and (item['versionShortLibelle'] == lan)

# versionProg :
#       1 = Version langue URL
#       2 = Version inverse de langue URL
#       3 = VO-STF VOSTF
#       8 = VF-STMF ST sourds/mal
def match(item, chosen_quality, vost=False):
    return (item['VQU'] == chosen_quality) and ((vost and item['versionProg'] == '3') or (not vost and item['versionProg'] == '1'))


def load_json(url, params=None):
    r = requests.get(url, params=params, headers=headers)
    return r.json()


# cosmetic parse functions
def parse_date(datestr):
    date = None
    # workaround for datetime.strptime not working (NoneType ???)
    try:
        date = datetime.datetime.strptime(datestr, '%d/%m/%Y %H:%M:%S')
    except TypeError:
        date = datetime.datetime.fromtimestamp(time.mktime(time.strptime(datestr, '%d/%m/%Y %H:%M:%S')))
    return date


def parse_views(viewsstr):
    views = float(viewsstr)
    human_readable_unit = ''
    for unit in ['', 'K', 'M', 'B']:
        div_views = (views / 1000)
        if div_views >= 1.0:
            views = div_views
        else:
            human_readable_unit = unit
            break
    return '{v:.1f}'.format(v=views).rstrip('0').rstrip('.') + human_readable_unit


if __name__ == '__main__':
    plugin.run()
