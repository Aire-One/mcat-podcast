#!/bin/python


#
# Tool for Monstercat Podcast !
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#


import getopt, sys
import urllib.request
import xml.etree.ElementTree as ET

url = "https://www.monstercat.com/podcast/feed.xml"

class Podcast :
    title = ''
    author = ''
    subtitle = ''
    summary = ''
    image = ''
    enclosure = ''
    guid = ''
    pubDate = ''
    duration = ''
    explicit = ''

    def __str__ (self) :
        return self.title
    def __repr__ (self) :
        return self.__str__ ()

    def prettyStr (self) :
        return self.title + " :\n" + self.subtitle

def update_progress (size, total) :
    progress = (size / total) * 100
    bar_size = 30
    past = int (progress * bar_size / 100)
    remaining = bar_size - past
    print ('\r[{0}] {1}%'.format ('#'*past + '-'*remaining, round (progress)), end='')


def usage () :
    print ("""
    Tool for Monstercat Podcast !

usage : mcat-podcast.py -hlsd <options>
options :
    -h --help : print this help
    -l --list : give all episodes title
    -s --summary : provide the summary of the episodes (contains tracklist and some other cool information)
    -d --download : download the specified podcast""")


def getFeeds () :
    try :
        with urllib.request.urlopen (
            urllib.request.Request(
                url,
                data = None,
                headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:52.0) Gecko/20100101 Firefox/52.0'})
        ) as response :
            feeds = []
            root = ET.fromstring (response.read ())
            for i in root.iter ('item') :
                p = Podcast ()
                p.title = i.find ('title').text
                p.author = i.find ('{http://www.itunes.com/dtds/podcast-1.0.dtd}author').text
                p.subtitle = i.find ('{http://www.itunes.com/dtds/podcast-1.0.dtd}subtitle').text
                p.summary = i.find ('{http://www.itunes.com/dtds/podcast-1.0.dtd}summary').text
                p.image = i.find ('{http://www.itunes.com/dtds/podcast-1.0.dtd}image').get ('href')
                p.enclosure = i.find ('enclosure').get ('url')
                p.guid = i.find ('guid').text
                p.pubDate = i.find ('pubDate').text
                p.duration = i.find ('{http://www.itunes.com/dtds/podcast-1.0.dtd}duration').text
                p.explicit = i.find ('{http://www.itunes.com/dtds/podcast-1.0.dtd}explicit').text
                feeds.append (p)
            return feeds
    except :
        print ('Can\'t get feeds ! :c')
        sys.exit (1)

def getPodcast (keys) :
    feeds = getFeeds ()
    podcasts = []
    if not isinstance (keys, list) :
        keys = [keys]

    for f in feeds :
        for k in keys :
            if k in f.title or k in f.subtitle :
                podcasts.append (f)

    return podcasts

def getlist () :
    for f in reversed (getFeeds ()) :
        print (f.title, f.subtitle)

def tracklist (ep) :
    for podcast in getPodcast (ep) :
        print (podcast.title, podcast.subtitle)
        print ("Summary :\n", podcast.summary)
        print ("\n")

def download (ep) :
    for podcast in getPodcast (ep) :
        with urllib.request.urlopen (
            urllib.request.Request (
                podcast.enclosure,
                data = None,
                headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:52.0) Gecko/20100101 Firefox/52.0'})
        ) as r, open (podcast.enclosure.split('/')[-1], 'wb') as out_file :
            length = r.getheader('content-length')
            if length :
                length = int (length)
                blocksize = max (4096, length//100)
            else : # if header can't be read
                blocksize = 1000000 # just made something up
            size = 0
            while True :
                buf = r.read (blocksize)
                if not buf :
                    break
                out_file.write (buf)
                size += len (buf)
                if length :
                    update_progress (size, length)
            print ('')

def main () :

    try :
        opts, args = getopt.getopt(sys.argv[1:], "hls:d:", ["help", "list", "summary=", "download="])
    except getopt.GetoptError as err :
        print (err)
        usage ()
        sys.exit (2)

    if len (opts) == 0 :
        usage ()
        sys.exit ()

    for o, a in opts :
        if o in ("-h", "--help") :
            usage ()
            sys.exit ()
        elif o in ("-l", "--list") :
            getlist ()
        elif o in ("-s", "--summary") :
            tracklist (a)
        elif o in ("-d", "--download") :
            download (a)
        else :
            assert False, "unhandled option"

if __name__ == "__main__" :
    main ()
