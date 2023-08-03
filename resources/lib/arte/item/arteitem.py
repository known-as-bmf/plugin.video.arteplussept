"""
Various Arte items : basic Arte item, Arte Colleciton, Arte Live Item, etc..
"""

import html
# pylint: disable=import-error
from xbmcswift2 import actions
# pylint: disable=cyclic-import
from addon import plugin
# the goal is to break/limit this dependency as much as possible
from resources.lib import mapper
from resources.lib import utils


class ArteItem:
    """
    Item of Arte TV or HBBTV API. It may be a video, a collection or anything.
    It aims at being mapped into XBMC ListItem.
    """

    PREFERED_KINDS = ['TV_SERIES', 'MAGAZINE']

    def __init__(self, json_dict):
        self.json_dict = json_dict


    def format_title_and_subtitle(self):
        """Build string for menu entry thanks to title and optionally subtitle"""
        title = self.json_dict.get('title')
        subtitle = self.json_dict.get('subtitle')
        label = f"[B]{html.unescape(title)}[/B]"
        # suffixes
        if subtitle:
            label += f" - {html.unescape(subtitle)}"
        return label


    def map_artetv_item(self):
        """
        Return video menu item to show content from Arte TV API.
        Manage specificities of various types : playlist, menu or video items
        """
        item = self.json_dict
        program_id = item.get('programId')
        kind = item.get('kind')
        if isinstance(kind, dict) and kind.get('code', False):
            kind = kind.get('code')
        if kind == 'EXTERNAL':
            return None

        if self._is_playlist():
            if kind in self.PREFERED_KINDS:
                #content_type = Content.PLAYLIST
                path = plugin.url_for('play_collection', kind=kind, collection_id=program_id)
                is_playable = True
            else:
                #content_type = Content.MENU_ITEM
                path = plugin.url_for('display_collection', kind=kind, program_id=program_id)
                is_playable = False
        else:
            #content_type = Content.VIDEO
            path = plugin.url_for('play', kind=kind, program_id=program_id)
            is_playable = True

        return self.map_artetv_item_new(path, is_playable)

    def map_artetv_item_new(self, path, is_playable):
        """
        Return video menu item to show content from Arte TV API.
        Generic method that tqke variables mapping in inputs.
        :rtype dict[str, Any] | None: To be used in
        https://romanvm.github.io/Kodistubs/_autosummary/xbmcgui.html#xbmcgui.ListItem.setInfo
        """
        item = self.json_dict
        program_id = item.get('programId')
        label = self.format_title_and_subtitle()
        kind = item.get('kind')
        duration = item.get('durationSeconds')
        airdate = item.get('beginsAt') # broadcastBegin
        if airdate is not None:
            airdate = str(utils.parse_date_artetv(airdate))

        fanart_url = ""
        thumbnail_url = ""
        if item.get('images') and item.get('images')[0] and item.get('images')[0].get('url'):
            # Remove query param type=TEXT to avoid title embeded in image
            fanart_url = item.get('images')[0].get('url').replace('?type=TEXT', '')
            # Set same image for fanart and thumbnail to spare network bandwidth
            # and business logic easier to maintain
            #if item.get('images')[0].get('alternateResolutions'):
            #    smallerImage = item.get('images')[0].get('alternateResolutions')[3]
            #    if smallerImage and smallerImage.get('url'):
            #        thumbnailUrl = smallerImage.get('url').replace('?type=TEXT', '')
        if not fanart_url:
            fanart_url = item.get('mainImage').get('url').replace('__SIZE__', '1920x1080')
        thumbnail_url = fanart_url

        progress = self._get_progress()
        time_offset = item.get('lastviewed') and item.get('lastviewed').get('timecode') or 0

        if isinstance(kind, dict) and kind.get('code', False):
            kind = kind.get('code')
        if kind == 'EXTERNAL':
            return None

        return {
            'label': label,
            'path': path,
            'thumbnail': thumbnail_url,
            'is_playable': is_playable, # item.get('playable') # not show_video_streams
            'info_type': 'video',
            'info': {
                'title': item.get('title'),
                'duration': duration,
                #'genre': item.get('genrePresse'),
                'plot': item.get('description'),
                'plotoutline': item.get('shortDescription'),
                # year is not correctly used by kodi :(
                # the aired year will be used by kodi for production year :(
                # 'year': int(config.get('productionYear')),
                #'country': [country.get('label') for country in item.get('productionCountries', [])],
                #'director': item.get('director'),
                #'aired': airdate
                'playcount': '1' if progress >= 0.95 else '0',
            },
            'properties': {
                'fanart_image': fanart_url,
                # ResumeTime and TotalTime deprecated. Use InfoTagVideo.setResumePoint() instead.
                'ResumeTime': str(time_offset),
                'TotalTime': str(duration),
                'StartPercent': str(progress * 100)
            },
            'context_menu': [
                (plugin.addon.getLocalizedString(30023),
                    actions.background(plugin.url_for(
                        'add_favorite', program_id=program_id, label=label))),
                (plugin.addon.getLocalizedString(30024),
                    actions.background(plugin.url_for(
                        'remove_favorite', program_id=program_id, label=label))),
                (plugin.addon.getLocalizedString(30035),
                    actions.background(plugin.url_for(
                        'mark_as_watched', program_id=program_id, label=label))),
            ],
        }

    def _is_playlist(self):
        """Return True if program_id is a str starting with PL- or RC-."""
        is_playlist_var = False
        program_id = self.json_dict.get('programId')
        if isinstance(program_id, str):
            is_playlist_var = program_id.startswith('RC-') or program_id.startswith('PL-')
        return is_playlist_var


    def _get_progress(self):
        """
        Return item progress or 0 as float.
        Never None, even if lastviewed or item is None.
        """
        # pylint raises that it is not snake_case. it's in uppercase, because it's a constant
        # pylint: disable=invalid-name
        DEFAULT_PROGRESS = 0.0
        if not self.json_dict:
            return DEFAULT_PROGRESS
        if not self.json_dict.get('lastviewed'):
            return DEFAULT_PROGRESS
        if not self.json_dict.get('lastviewed').get('progress'):
            return DEFAULT_PROGRESS
        return float(self.json_dict.get('lastviewed').get('progress'))



class ArteLiveItem(ArteItem):
    """
    Arte Live is slightly different from standard item, because it is stream from Arte TV API only.
    It cannot be part of a playlist.
    Its label is prefixed with LIVE.
    """

    def format_title_and_subtitle(self):
        """Orange prefix LIVE for live stream"""
        return f"[COLOR ffffa500]LIVE[/COLOR] - {super().format_title_and_subtitle()}"

    def map_live_video(self, quality, audio_slot):
        """Return menu entry to watch live content from Arte TV API"""
        # program_id = item.get('id')
        item = self.json_dict
        attr = item.get('attributes')
        meta = attr.get('metadata')

        duration = meta.get('duration').get('seconds')

        fanart_url = ""
        thumbnail_url = ""
        if meta.get('images') and meta.get('images')[0] and meta.get('images')[0].get('url'):
            # Remove query param type=TEXT to avoid title embeded in image
            fanart_url = meta.get('images')[0].get('url').replace('?type=TEXT', '')
            thumbnail_url = fanart_url
            # Set same image for fanart and thumbnail to spare network bandwidth
            # and business logic easier to maintain
            #if item.get('images')[0].get('alternateResolutions'):
            #    smallerImage = item.get('images')[0].get('alternateResolutions')[3]
            #    if smallerImage and smallerImage.get('url'):
            #        thumbnailUrl = smallerImage.get('url').replace('?type=TEXT', '')
        stream_url=mapper.map_playable(
            attr.get('streams'), quality, audio_slot, mapper.match_artetv).get('path')

        return {
            'label': ArteLiveItem(meta).format_title_and_subtitle(),
            'path': plugin.url_for('play_live', stream_url=stream_url),
            # playing the stream from program id makes the live starts from the beginning of the video
            # while it starts the video like the live tv, with the above
            #  'path': plugin.url_for('play', kind='SHOW', program_id=programId.replace('_fr', '')),
            'thumbnail': thumbnail_url,
            'is_playable': True, # not show_video_streams
            'info_type': 'video',
            'info': {
                'title': meta.get('title'),
                'duration': duration,
                #'genre': item.get('genrePresse'),
                'plot': meta.get('description'),
                #'plotoutline': meta.get('shortDescription'),
                # year is not correctly used by kodi :(
                # the aired year will be used by kodi for production year :(
                # 'year': int(config.get('productionYear')),
                #'country': [country.get('label') for country in item.get('productionCountries', [])],
                #'director': item.get('director'),
                #'aired': airdate
                'playcount': '0',
            },
            'properties': {
                'fanart_image': fanart_url,
            }
        }


class ArteCollectionItem(ArteItem):
    """
    A collection item is different from a standard video item,
    because it opens a new menu populated with video or collection items
    instead of playing a video.
    """

    def map_collection_as_menu_item(self):
        """Map JSON item to menu entry to access playlist content"""
        item = self.json_dict
        program_id = item.get('programId')
        kind = item.get('kind')

        return {
            'label': self.format_title_and_subtitle(),
            'path': plugin.url_for('display_collection', kind=kind, collection_id=program_id),
            'thumbnail': item.get('imageUrl'),
            'info': {
                'title': item.get('title'),
                'plotoutline': item.get('teaserText')
            }
        }
