from xbmcswift2 import xbmc

from . import api
from . import mapper

def build_home_page(plugin, cached_categories, settings):
    addon_menu = [
        mapper.create_search_item(),
    ]
    try:
        live_stream_data = api.program_video(settings.language, 'LIVE')
        live_stream_item = mapper.map_live_video(live_stream_data, settings.quality, '1')
        addon_menu.append(live_stream_item)
    except:
        xbmc.log("Unable to build live stream item with lang:{ln} quality:{qlt}".format(ln=settings.language, qlt=settings.quality))

    arte_home = api.page(settings.language)
    for zone in arte_home.get('zones'):
        menu_item = mapper.map_zone_to_item(zone, cached_categories)
        if menu_item:
            addon_menu.append(menu_item)
    return addon_menu


def build_api_category(category_code, settings):
    category = [mapper.map_category_item(item, category_code) for item in
            api.category(category_code, settings.language)]

    return category


def get_cached_category(category_title, most_viewed_categories):
    return most_viewed_categories[category_title]


def build_favorites(plugin, settings):
    return [mapper.map_artetv_video(item) for item in
            api.get_favorites(plugin, settings.language, settings.username, settings.password) or
            # display an empty list in case of error. error should be display in a notification
            []]

def add_favorite(plugin, usr, pwd, program_id, label):
    if 200 == api.add_favorite(plugin, usr, pwd, program_id):
        msg = plugin.addon.getLocalizedString(30025).format(label=label)
        plugin.notify(msg=msg, image='info')
    else:
        msg = plugin.addon.getLocalizedString(30026).format(label=label)
        plugin.notify(msg=msg, image='error')

def remove_favorite(plugin, usr, pwd, program_id, label):
    if 200 == api.remove_favorite(plugin, usr, pwd, program_id):
        msg = plugin.addon.getLocalizedString(30027).format(label=label)
        plugin.notify(msg=msg, image='info')
    else:
        msg = plugin.addon.getLocalizedString(30028).format(label=label)
        plugin.notify(msg=msg, image='error')


def build_last_viewed(plugin, settings):
    return [mapper.map_artetv_video(item) for item in
            api.get_last_viewed(plugin, settings.language, settings.username, settings.password) or
            # display an empty list in case of error. error should be display in a notification
            []]

def purge_last_viewed(plugin, usr, pwd):
    if 200 == api.purge_last_viewed(plugin, usr, pwd):
        plugin.notify(msg=plugin.addon.getLocalizedString(30031), image='info')
    else:
        plugin.notify(msg=plugin.addon.getLocalizedString(30032), image='error')


def build_mixed_collection(kind, collection_id, settings):
    return [mapper.map_generic_item(item, settings.show_video_streams) for item in
            api.collection(kind, collection_id, settings.language)]


def build_video_streams(program_id, settings):
    item = api.video(program_id, settings.language)

    if item is None:
        raise RuntimeError('Video not found...')

    program_id = item.get('programId')
    kind = item.get('kind')

    return mapper.map_streams(item, api.streams(kind, program_id, settings.language), settings.quality)


def build_stream_url(plugin, kind, program_id, audio_slot, settings):
    # first try with content
    program_stream = api.streams(kind, program_id, settings.language)
    if program_stream:
        return mapper.map_playable(program_stream, settings.quality, audio_slot, mapper.match_hbbtv)
    # second try to fallback clip
    clip_stream = api.streams('CLIP', program_id, settings.language)
    if clip_stream:
        return mapper.map_playable(clip_stream, settings.quality, audio_slot, mapper.match_hbbtv)
    # otherwise raise the error
    msg = plugin.addon.getLocalizedString(30029)
    plugin.notify(msg=msg.format(strm=program_id, ln=settings.language), image='error')


def search(plugin, settings):
    query = get_search_query(plugin)
    if not query:
        plugin.end_of_directory(succeeded=False)
    return mapper.map_cached_categories(
        api.search(settings.language, query))

def get_search_query(plugin):
    searchStr = ''
    keyboard = xbmc.Keyboard(searchStr, plugin.addon.getLocalizedString(30012))
    keyboard.doModal()
    if False == keyboard.isConfirmed():
        return
    searchStr = keyboard.getText()
    if len(searchStr) == 0:
        return
    else:
        return searchStr