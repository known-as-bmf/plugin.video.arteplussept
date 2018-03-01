
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


# global declarations
# plugin stuff
plugin = Plugin()


class PluginInformation:
    name = plugin.name
    version = plugin.addon.getAddonInfo('version')


# settings stuff
languages = [
    {'short': 'fr', 'long': 'fr_FR'},
    {'short': 'de', 'long': 'de_DE'},
    {'short': 'en', 'long': 'en_GB'},
    {'short': 'es', 'long': 'es_ES'},
    {'short': 'pl', 'long': 'pl_PL'}
]
qualities = ['SQ', 'EQ', 'HQ', 'MQ']

# defaults to fr
language = languages[plugin.get_setting('lang', int)] or languages[0]
# defaults to SQ
quality = qualities[plugin.get_setting('quality', int)] or qualities[0]

# my imports
import api
import mapper


@plugin.route('/')
def index():
    return [mapper.map_index_item(app_name, config) for app_name, config in api.apps().iteritems()]


@plugin.route('/app/<app_name>/<teasers_path>', name='app')
def app(app_name, teasers_path):
    filters = api.filters(app_name)

    return [mapper.map_app_item(app_name, config, teasers_path) for config in filters]


@plugin.route('/sub_app/<app_name>', name='sub_app')
def sub_app(app_name):
    filters = api.filters(app_name)

    return mapper.map_sub_app_items(filters)


@plugin.route('/teaser/<teaser>/<teasers_path>', name='teaser')
def teaser(teasers_path, teaser):
    teasers = api.teasers(teasers_path, language.get('short', 'fr'))

    return [mapper.map_teaser_item(item) for item in teasers.get(teaser)]


@plugin.route('/collection/<collection_id>', name='collection')
def collection(collection_id):
    plugin.set_content('tvshows')
    items = [mapper.map_video(item) for item in api.collection(
        collection_id, language.get('short', 'fr'))]
    return plugin.finish(items)


@plugin.route('/videos/<path>', name='videos')
def videos(path):
    plugin.set_content('tvshows')
    items = [mapper.map_video(item) for item in api.videos(
        path, language.get('short', 'fr'))]
    return plugin.finish(items)


@plugin.route('/play/<kind>/<program_id>', name='play')
def play(kind, program_id):
    streams = api.streams(kind, program_id, language.get('short', 'fr'))

    return plugin.set_resolved_url(mapper.map_playable(streams, quality))


# plugin bootstrap
if __name__ == '__main__':
    plugin.run()
