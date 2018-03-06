from addon import plugin

import hof
import utils


def map_index_item(app_name, config):
    return {
        'label': utils.localized_string(config.get('name')),
        'path': plugin.url_for('app', app_name=app_name, teasers_path=config.get('data_url'))
    }


def map_app_item(app_name, config, teasers_path):
    item = {
        'label': utils.localized_string(config.get('label'))
    }
    app_type = config.get('type')
    if(app_type == 'button'):
        item.update(_map_app_button(config, teasers_path))
    if(app_type == 'list'):
        item.update(_map_app_list(app_name, config, teasers_path))
    return item


def _map_app_button(config, teasers_path):
    teaser = hof.get_property(config, 'data.teasers')
    url = hof.get_property(config, 'data.url')
    if teaser:
        return {'path': plugin.url_for('teaser', teasers_path=teasers_path, teaser=teaser)}
    elif url:
        # url contains a leading "/" we dont want
        return {'path': plugin.url_for('videos', path=url[1:])}


def _map_app_list(app_name, config, teasers_path):
    teaser = hof.get_property(config, 'data.teasers')
    if teaser:
        return {'path': plugin.url_for('teaser', teasers_path=teasers_path, teaser=teaser)}
    # rubrique
    else:
        return {'path': plugin.url_for('sub_app', app_name=app_name)}


def map_sub_app_items(config):
    sub_category = hof.find(lambda app: hof.get_property(
        app, 'data.content'), config) or {}
    content = hof.get_property(sub_category, 'data.content')

    return [{
        'label': utils.localized_string(category.get('label')),
        'path': plugin.url_for('videos', path=category.get('url'))
    } for category in content]


def map_generic_item(config):
    programId = config.get('programId')
    is_item = programId is not None

    if is_item:
        is_playlist = programId.startswith('RC-') or programId.startswith('PL-')
        if not is_playlist:
            return map_video(config)
        else:
            return {
                'label': utils.format_title_and_subtitle(config.get('title'), config.get('subtitle')),
                'path': plugin.url_for('collection', collection_id=programId),
                'thumbnail': config.get('imageUrl'),
                'info': {
                    'title': config.get('title'),
                    'plotoutline': config.get('teaserText')
                }
            }
    else:
        return {
            'label': utils.localized_string(config.get('label')),
            'path': plugin.url_for('videos', path=config.get('url'))
        }


def map_video(config):
    programId = config.get('programId')
    kind = config.get('kind')
    duration = int(config.get('duration') or 0) * \
        60 or config.get('durationSeconds')

    return {
        'label': utils.format_title_and_subtitle(config.get('title'), config.get('subtitle')),
        'path': plugin.url_for('play', kind=kind, program_id=programId),
        'thumbnail': config.get('imageUrl'),
        'is_playable': True,
        'info_type': 'video',
        'info': {
            'title': config.get('title'),
            'duration': duration,
            'genre': config.get('genrePresse'),
            'plot': config.get('shortDescription'),
            'plotoutline': config.get('teaserText'),
            # year is not correctly used by kodi :(
            # the aired year will be used by kodi for production year :(
            #'year': int(config.get('productionYear')),
            'country': [country.get('label') for country in config.get('productionCountries', [])],
            'director': config.get('director'),
            #'aired': str(airdate)
        },
        'properties': {
            'fanart_image': config.get('imageUrl'),
        }
    }


def map_playable(streams, quality):
    stream = None
    for q in [quality] + [i for i in ['SQ', 'EQ', 'HQ', 'MQ'] if i is not quality]:
        stream = hof.find(lambda s: match(s, q), streams)
        if stream:
            break
    return {
        'path': stream.get('url')
    }


def match(item, quality):
    return item.get('quality') == quality and item.get('audioSlot') == 1
