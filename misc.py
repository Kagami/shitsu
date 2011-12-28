import re
import urllib2
try:
    from lxml import etree
except ImportError:
    pass


url_re = re.compile('https?://[^ >]+')


def force_unicode(string, encoding='utf-8'):
    if type(string) is str:
        string = string.decode(encoding)
    if type(string) is not unicode:
        string = unicode(string)
    return string


request_headers = {
    'User-Agent': ('Mozilla/5.0 (Windows NT 5.1; rv:8.0) '
                   'Gecko/20100101 Firefox/8.0')
}

def readUrl(url):
    request = urllib2.Request(url.encode('utf-8'), None, request_headers)
    try:
        return urllib2.urlopen(request, None, 3).read()
    except:
        return ''


max_title_length = 150
blacklisted_domains = (
    'localhost', '127\.0\.0\.1',
    'danbooru\.donmai\.us', 'gelbooru\.com', 'konachan\.com',
)
blacklisted_domains_re = map(
    lambda d: re.compile('https?://(www\.)?' + d),
    blacklisted_domains)

def getTitle(url):
    for regexp in blacklisted_domains_re:
        if regexp.match(url) is not None:
            return
    data = readUrl(url)
    if not data: return
    try:
        data = data.decode('utf-8')
    except:
        try:
            data = data.decode('cp1251')
        except:
            pass
    try:
        title = etree.HTML(data).find('.//title').text.strip()
    except:
        return
    title = title.replace('\t', '').replace('\n', ' ')
    if len(title) > max_title_length:
        title = title[:max_title_length] + u'\u2026'
    return title
