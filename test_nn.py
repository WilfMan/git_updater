import os
import traceback
import urllib2
from lxml import etree
from base64 import b64encode
import subprocess
import time

dir_ = os.path.dirname(__file__)
habr = ['habrahabr', 'https://habrahabr.ru/rss/all/']
geek = ['geektimes', 'https://geektimes.ru/rss/all/']
urls = [habr, geek]


def get_full_path(*args):
    return os.path.join(dir_, *args)


def get_old_new(feed):
    try:
        with open(get_full_path('.temp_%s' % feed)) as t:
            old = t.read()
        return old.strip().split(',')
    except:
        return []


def set_old(data, feed):
    with open(get_full_path('.temp_%s' % feed), 'w') as t:
        t.write(','.join(data))


def read_rss(feed, url):
    old = get_old_new(feed)
    data = urllib2.urlopen(url).read()
    e = etree.fromstring(data, etree.XMLParser(recover=True, strip_cdata=False))
    news = e.findall('.//item')
    new = []
    for i in news:
        title = i.find('.//title').text
        href = i.find('.//guid').text
        new.append(b64encode(href))
        if b64encode(href) in old:
            continue
        subprocess.call(['notify-send', feed, '\n' + title + '\n' + href, ])
    set_old(new, feed)


def main():
    while 1:
        for i in urls:
            try:
                print 'read'
                read_rss(*i)
            except KeyboardInterrupt:
                exit(0)
            except:
                traceback.print_exc()
        time.sleep(60)


if __name__ == '__main__':
    main()
