
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
## plugin stuff
plugin = Plugin()
class PluginInformation:
  name = plugin.name
  version = plugin.addon.getAddonInfo('version')

## settings stuff
languages = [
  {'short': 'fr', 'long': 'fr_FR'},
  {'short': 'de', 'long': 'de_DE'},
  {'short': 'en', 'long': 'en_GB'},
  {'short': 'es', 'long': 'es_ES'},
  {'short': 'pl', 'long': 'pl_PL'}
]
language = languages[plugin.get_setting('lang', int)] or languages[0]


# my imports
import api
import mapper


@plugin.route('/')
def index():
  return [mapper.map_index_item(name, config) for name, config in api.apps().iteritems()]


@plugin.route('/app/<name>', name='app')
def app(name):
  filters = api.filters(name)

  return [mapper.map_app_item(config) for config in filters]

@plugin.route('/app/<name>/<sub>', name='sub_app')
def sub_app(name, sub):
  filters = api.filters(name)

  return [mapper.map_app_item(config) for config in filters]


@plugin.route('/teasers/<name>', name='teasers')
def teasers(name):
  teasers = api.teasers(name, language.get('short', 'fr'))


@plugin.route('/listing/<url>', name='listing')
def listing(url):
  pass


# plugin bootstrap
if __name__ == '__main__':
  plugin.run()
