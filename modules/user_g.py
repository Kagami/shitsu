import urllib
import re
import utils
from json import loads


def main(bot, args):
    """g [site] <query>
    Search on google.
    Available sites shortcuts:
    v - ru.wikipedia.org
    w - en.wikipedia.org
    lm - lurkmore
    wa - world-art.ru
    ad - anidb.info
    ed - encyclopediadramatica
    y - youtube.com
    """
    if not args: return

    if args[0] == 'v':
        site = 'ru.wikipedia.org'
    elif args[0] == 'w':
        site = 'en.wikipedia.org'
    elif args[0] == 'lm':
        site = 'lurkmore.ru'
    elif args[0] == 'wa':
        site = 'world-art.ru'
    elif args[0] == 'ad':
        site = 'anidb.info'
    elif args[0] == 'ed':
        site = 'encyclopediadramatica.com'
    elif args[0] == 'y':
        site = 'youtube.com'
    else:
        site = ''
    if site:
        if len(args) == 1:
            return
        site = 'site:%s ' % site
        args = args[1:]

    return google(site + ' '.join(args))


def google(query):
    query = urllib.quote(query.encode('utf-8'))
    data = utils.readUrl('http://ajax.googleapis.com/ajax/services/search/web?v=1.0&q=%s&hl=ru' %query)
    if not data: return "can't get data"

    try:
        convert = loads(data)
        results = convert['responseData']['results']
        if not results: return 'not found'

        url = urllib.unquote(results[0]['url'])
        title = results[0]['titleNoFormatting']
        content = results[0]['content']
        text = '%s\n%s\n%s' %(title, content, url)

        text = re.sub('<b>|</b>', '', text)
        text = re.sub('   ', '\n', text)

        return text
    except:
        return 'error'
