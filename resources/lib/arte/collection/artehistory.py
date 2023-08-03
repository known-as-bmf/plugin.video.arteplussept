from resources.lib import api
from resources.lib import user
from resources.lib.arte.collection import artecollection as ac

# pylint: disable=import-error
from xbmcswift2 import actions
# pylint: disable=import-error
from xbmcswift2 import xbmcgui


class ArteHistory:

    def __init__(self, plugin, settings):
        self.plugin = plugin
        self.settings = settings

    def build_item(self, label):
        """Return menu entry to access user history
        with an additional command to flush user history"""
        return {
            'label': label,
            'path': self.plugin.url_for('last_viewed_default'),
            'context_menu': [
                (self.plugin.addon.getLocalizedString(30030),
                    actions.background(self.plugin.url_for('purge_last_viewed')))
            ]
        }


    def build_menu(self, page):
        """Build the menu of user history"""
        return ac.ArteCollection(api.get_last_viewed_class(
            self.settings.language,
            user.get_cached_token(self.plugin, self.settings.username),
            page)).to_menu(self.plugin, 'last_viewed')


    def purge(self):
        """Flush user history and notify about success or failure"""
        purge_confirmed = xbmcgui.Dialog().yesno(
            self.plugin.addon.getLocalizedString(30030),
            self.plugin.addon.getLocalizedString(30033),
            autoclose=10000)
        if purge_confirmed:
            if 200 == api.purge_last_viewed(user.get_cached_token(self.plugin, self.settings.username)):
                self.plugin.notify(msg=self.plugin.addon.getLocalizedString(30031), image='info')
            else:
                self.plugin.notify(msg=self.plugin.addon.getLocalizedString(30032), image='error')
