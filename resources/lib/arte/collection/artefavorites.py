from resources.lib import api
from resources.lib import user
from resources.lib.arte.collection import artecollection as ac

# pylint: disable=import-error
from xbmcswift2 import actions
# pylint: disable=import-error
from xbmcswift2 import xbmcgui

class ArteFavorites:

    def __init__(self, plugin, settings):
        self.plugin = plugin
        self.settings = settings


    def build_item(self, label):
        """Return menu entry to access user favorites"""
        return {
            'label': label,
            'path': self.plugin.url_for('favorites_default'),
            'context_menu': [
                (self.plugin.addon.getLocalizedString(30040),
                    actions.background(self.plugin.url_for('purge_favorites')))
            ]
        }


    def build_menu(self, page):
        """Build the menu for user favorites thanks to API call"""
        return ac.ArteCollection(api.get_favorites_class(
            self.settings.language,
            user.get_cached_token(self.plugin, self.settings.username),
            page)).to_menu(self.plugin, 'favorites')


    def add_favorite(self, program_id, label):
        """Add content program_id to user favorites.
        Notify about completion success or failure with label."""
        if 200 == api.add_favorite(user.get_cached_token(self.plugin, self.settings.username), program_id):
            msg = self.plugin.addon.getLocalizedString(30025).format(label=label)
            self.plugin.notify(msg=msg, image='info')
        else:
            msg = self.plugin.addon.getLocalizedString(30026).format(label=label)
            self.plugin.notify(msg=msg, image='error')


    def remove_favorite(self, program_id, label):
        """Remove content program_id from user favorites.
        Notify about completion success or failure with label."""
        if 200 == api.remove_favorite(user.get_cached_token(self.plugin, self.settings.username), program_id):
            msg = self.plugin.addon.getLocalizedString(30027).format(label=label)
            self.plugin.notify(msg=msg, image='info')
        else:
            msg = self.plugin.addon.getLocalizedString(30028).format(label=label)
            self.plugin.notify(msg=msg, image='error')


    def purge(self):
        """Flush user favorites and notify about success or failure"""
        purge_confirmed = xbmcgui.Dialog().yesno(
            self.plugin.addon.getLocalizedString(30040),
            self.plugin.addon.getLocalizedString(30043),
            autoclose=10000)

        if purge_confirmed:
            if 200 == api.purge_favorites(user.get_cached_token(self.plugin, self.settings.username)):
                self.plugin.notify(msg=self.plugin.addon.getLocalizedString(30041), image='info')
            else:
                self.plugin.notify(msg=self.plugin.addon.getLocalizedString(30042), image='error')
