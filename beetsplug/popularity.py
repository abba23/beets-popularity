# -*- coding: utf-8 -*-

from beets.plugins import BeetsPlugin
from beets.dbcore import types
import beets.ui as ui
import json
import requests


class Popularity(BeetsPlugin):

    def __init__(self):
        super(Popularity, self).__init__()
        self.item_types = {'popularity': types.INTEGER}
        self.register_listener('write', self._on_write)
        self.API_URL = 'https://api.spotify.com/v1/search'

    def commands(self):
        command = ui.Subcommand('popularity',
                                help='fetch popularity values from Spotify',
                                aliases=['pop'])
        command.func = self._command
        command.parser.add_album_option()
        command.parser.add_option(
            '-n', '--nowrite', action='store_true',
            dest='nowrite', default=False,
            help='print the popularity values without storing them')
        return [command]

    def _command(self, lib, opts, args):
        # search library for items matching the query
        items = []
        if opts.album:
            albums = list(lib.albums(ui.decargs(args)))
            for album in albums:
                items += album.items()
        else:
            items = lib.items(ui.decargs(args))

        # query and set popularity value for all matching items
        for item in items:
            self._set_popularity(item, opts.nowrite)

    def _on_write(self, item, path, tags):
        # query and set popularity value for the item that is to be imported
        self._set_popularity(item, False)

    def _set_popularity(self, item, nowrite):
        # query Spotify API
        query = item.artist + ' ' + item.title
        payload = {'q': query, 'type': 'track', 'limit': '1'}
        response = requests.get(self.API_URL, params=payload)

        try:
            # raise an exception for bad response status codes
            response.raise_for_status()

            # load response as json
            response_json = json.loads(response.content)
            tracks = response_json["tracks"]["items"]

            # raise an exception if the query returned no tracks
            if not tracks:
                raise EmptyResponseError()

            popularity = tracks[0]["popularity"]
            self._log.info(
                u'{0.artist} - {0.album} - {0.title}: {1}', item, popularity)

            # store the popularity value as a flexible attribute
            if not nowrite:
                item.popularity = popularity
                item.store()

        except requests.exceptions.HTTPError:
            self._log.warning(u'Bad status code in response from Spotify API')
        except EmptyResponseError:
            self._log.debug(
                u'{0.title} - {0.artist} not found on Spotify', item)


class EmptyResponseError(Exception):
    pass
