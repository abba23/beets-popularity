# -*- coding: utf-8 -*-

from beets.plugins import BeetsPlugin
from beets.dbcore import types
import beets.ui as ui
import json
import requests
import re
import time

class Popularity(BeetsPlugin):
    apirequests = 0
    
# inital functions
    def __init__(self):
        super(Popularity, self).__init__()
        self.item_types = {'popularity': types.INTEGER}
        self.register_listener('write', self._on_write)
        self.API_URL = 'https://api.deezer.com/search'
        #self.API_URL = 'https://api.spotify.com/v1/search'

    def commands(self):
        command = ui.Subcommand('popularity',
                                help='fetch popularity values',
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
    
# helper functions
    def _replace_brackets(self, string):
        # replace all brackets and its content within the Title
        string = re.sub(r'\(.*?\)', '', string)
        string = re.sub(r'\[.*?\]', '', string)
        string = re.sub('\s+', ' ', string).strip()
        return string
    
    def _has_brackets(self, string):
        # replace true if string contains brackets
        brackets = ["(", ")", "[", "]"]
        has_brackets = False
        if any(bracket in string for bracket in brackets):
            has_brackets = True
        return has_brackets
    
# request functions
    def _try_api_request(self, item, nowrite, query):
        payload = {'q': query, 'order': 'RANKING'}
        #payload = {'q': query, 'type': 'track', 'limit': '1'}
        response = requests.get(self.API_URL, params=payload)
        
        # sleep for 3 seconds if 50 api requests were executed due to deezers api limit that says: "limited to 50 requests / 5 seconds"
        if self.apirequests == 50:
            self.apirequests = 0
            time.sleep(2)
        self.apirequests += 1
        
        try:
            # raise an exception for bad response status codes
            response.raise_for_status()

            # load response as json
            response_json = json.loads(response.text)
            tracks = response_json["data"]
            #tracks = response_json["tracks"]["items"]

            # raise an exception if the query returned no tracks
            if not tracks:
                popularity_found = False
                raise EmptyResponseError()
            else:
                popularity_found = True
                popularity = round(tracks[0]["rank"] / 10000)
                #popularity = tracks[0]["popularity"]
                self._log.info(
                    u'{0.artist} - {0.title}: {1}', item, popularity)

                # store the popularity value as a flexible attribute
                if not nowrite:
                    item.popularity = popularity
                    item.store()

        except requests.exceptions.HTTPError:
            self._log.warning(u'Bad status code in API response')
        except EmptyResponseError:
            self._log.debug(
                u'{0.title} - {0.artist} not found', item)
        return popularity_found;
    
    def _api_requests(self, item, nowrite, artiststr, albumstr, titlestr):
        popularity_found = False
        # search with explicit tag statement and with album
        query = 'artist:"' + artiststr + '" album:"' + albumstr + '" track:"' + titlestr + '"'
        popularity_found = self._try_api_request(item, nowrite, query)
        if not popularity_found:
            # search without explicit tag statement and with album
            query = '"' + artiststr + ' - ' + albumstr + ' - ' + titlestr + '"'
            popularity_found = self._try_api_request(item, nowrite, query)
        if not popularity_found:
            # search with explicit tag statement and without album
            query = 'artist:"' + artiststr + '" track:"' + titlestr + '"'
            popularity_found = self._try_api_request(item, nowrite, query)
        if not popularity_found:
            # search without explicit tag statement and without album
            query = '"' + artiststr + ' - ' + titlestr + '"'
            popularity_found = self._try_api_request(item, nowrite, query)
        return popularity_found
    
    def _set_popularity(self, item, nowrite):
        # replacing specific minus from musicbrainz with that it can't find anything from the API (compare: http://unicode.scarfboy.com/?s=%E2%80%90 and  http://unicode.scarfboy.com/?s=-)
        # example: "blink‐182" will be "blink-182"
        replacechar = u'\u2010'
        artiststr = item.artist.replace(replacechar, "-")
        albumstr = item.album.replace(replacechar, "-")
        titlestr = item.title.replace(replacechar, "-")

        artistseperators = [" feat ", " feat. ", " & ", ", ", " , ", " featuring "]
        # delete featuring strings out of artist
        for artistseperator in artistseperators:
            allartiststr = artiststr.replace(artistseperator, " ")
        allartiststr = allartiststr.strip()

        popularity_found = False

        # first normal api request
        popularity_found = self._api_requests(item, nowrite, allartiststr, albumstr, titlestr)

        # without brackets in title:
        if not popularity_found:
            # check if title has brackets
            if self._has_brackets(titlestr):
                # try it without brackets in title
                replacedtitle = self._replace_brackets(titlestr)
                popularity_found =  self._api_requests(item, nowrite, allartiststr, albumstr, replacedtitle)

        # seperate artists:
        if not popularity_found:
            # check if there are multiple artists in artist tag
            seperateartists = re.split("|".join(artistseperators),artiststr)
            if len(seperateartists) > 1:
                # try it for each artist with brackets in title
                for seperateartist in seperateartists:
                    popularity_found = self._api_requests(item, nowrite, seperateartist, albumstr, titlestr)
                    if popularity_found:
                        break
                # try it for each artist if it has brackets in title
                if not popularity_found and self._has_brackets(titlestr):
                    replacedtitle = self._replace_brackets(titlestr)
                    for seperateartist in seperateartists:
                        popularity_found = self._api_requests(item, nowrite, seperateartist, albumstr, replacedtitle)
                        if popularity_found:
                            break

class EmptyResponseError(Exception):
    pass
