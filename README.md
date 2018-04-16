# beets-popularity

[Beets](http://beets.io/) plugin to store the popularity values from Deezer as flexible item attributes in the database

## Installation
*Note: this branch might not be compatible with Python 2.X  It is only tested with Python 3.5.3*

Using pip:

    $ pip install beets-popularity

Manually:

    $ git clone https://github.com/abba23/beets-popularity.git
    $ cd beets-popularity
    $ python setup.py install

You can then enable the plugin by [adding it to your `config.yaml`](https://beets.readthedocs.io/en/latest/plugins/index.html#using-plugins):

```yaml
plugins: popularity
```
## Usage
    $ beet popularity happy
    popularity: Bon Jovi - The Circle - Happy Now: 20
    popularity: The Doors - Strange Days - Unhappy Girl: 40
    popularity: Kygo - Cloud Nine - Happy Birthday: 59

## Options
| Option | |Description |
| ------ | ------ | ------ |
| -a | \-\-album | match albums instead of tracks |
| -n | \-\-nowrite | print the popularity values without storing them |

## Import
All imported songs will automatically have a popularity attribute and value assigned to them if the plugin is enabled.

## Query
As the popularity of a song is a value between 0 and 100, you could filter your library like this in order to list all tracks that have a popularity of at least 20:

    $ beet list -f '$artist - $title ($popularity)' popularity:20..
    Bon Jovi - Happy Now (20)
    The Doors - Unhappy Girl (40)
    Kygo - Happy Birthday (59)

This is especially useful in combination with the [Smart Playlist Plugin](https://beets.readthedocs.io/en/latest/plugins/smartplaylist.html). Adding this to your configuration would allow you to have continuously updated playlists of the most popular songs in your library:

```yaml
smartplaylist:
    playlist_dir: ~/Music/Playlists
    playlists:
        - name: popular.m3u
          query: 'popularity:70..'

        - name: popular_rock.m3u
          query: 'popularity:60.. genre:Rock'
```
