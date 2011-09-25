import urllib2
import re
from lxml import etree
import socket


headers = {}
headers['User-Agent'] = 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB;'+\
                        'rv:1.8.0.4) Gecko/20060508 Firefox/1.5.0.4'


def force_unicode(string, encoding='utf-8'):
    if type(string) is str:
        string = string.decode(encoding)
    if type(string) is not unicode:
        string = unicode(string)
    return string


def readUrl(url, cookies=None):
    try:
        socket.setdefaulttimeout(5)
        if cookies:
            headers['Cookie'] = cookies
        
        request = urllib2.Request(url.encode('utf-8'), None, headers)
        return urllib2.urlopen(request).read()
    except:
        return None


def getImgXML(img_url, img_src):
    img_url = re.sub('"|\'|<|>', '', img_url)
    img_src = re.sub('"|\'|<|>', '', img_src)
    img_url = re.sub('&', '&amp;', img_url)
    img_src = re.sub('&', '&amp;', img_src)

    return '<html xmlns=\'http://jabber.org/protocol/xhtml-im\'>' +\
           '<body xml:lang=\'en-US\' xmlns=\'http://www.w3.org/1999/xhtml\'>' +\
           '<a href=\'%s\'><img alt=\'img\' src=\'%s\' /></a>' %(img_url, img_src) +\
           '</body>' +\
           '</html>'


def getTitle(link):
    if re.search('^http://danbooru\.donmai\.us', link) or re.search('^http://(www\.)?gelbooru\.com', link):
        return ''
    else:
        try:
            data = readUrl(link)
            try:     data_enc = data.decode('utf-8')
            except:  data_enc = data.decode('cp1251')
            return etree.HTML(data_enc).find('*//title').text.strip().replace('\t', '').replace('\n', ' ')
        except:
            return ''

def makeTiny(link):
    url = 'http://tinyurl.com/api-create.php?url=%s' %link.encode('utf-8')
    try: return readUrl(url)
    except: return ''
