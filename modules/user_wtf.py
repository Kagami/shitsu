import urllib
import misc
from json import loads

def main(bot, args):
    '''wtf [text]\nDetect text language or show avialable languages if no text given.\nSee also: tr'''

    return detect_lang(' '.join(args))

def detect_lang(text):
	google_langs =\
		{ 'af':'Afrikaans','sq':'Albanian','am':'Amharic','ar':'Arabic','hy':'Armenian','az':'Azerbaijani','eu':'Basque'
		, 'be':'Belarusian','bn':'Bengali','bh':'Bihari','bg':'Bulgarian','my':'Burmese','ca':'Catalan','chr':'Cherokee'
		, 'zh':'Chinese','zh-CN':'Chinese_simplified','zh-TW':'Chinese_traditional','hr':'Croatian','cs':'Czech','da':'Danish'
		, 'dv':'Dhivehi','nl':'Dutch','en':'English','eo':'Esperanto','et':'Estonian','tl':'Filipino','fi':'Finnish'
		, 'fr':'French','gl':'Galician','ka':'Georgian','de':'German','el':'Greek','gn':'Guarani','gu':'Gujarati','iw':'Hebrew'
		, 'hi':'Hindi','hu':'Hungarian','is':'Icelandic','id':'Indonesian','iu':'Inuktitut','it':'Italian','ja':'Japanese'
		, 'kn':'Kannada','kk':'Kazakh','km':'Khmer','ko':'Korean','ku':'Kurdish','ky':'Kyrgyz','lo':'Laothian','lv':'Latvian'
		, 'lt':'Lithuanian','mk':'Macedonian','ms':'Malay','ml':'Malayalam','mt':'Maltese','mr':'Marathi','mn':'Mongolian'
		, 'ne':'Nepali','no':'Norwegian','or':'Oriya','ps':'Pashto','fa':'Persian','pl':'Polish','pt-PT':'Portuguese'
		, 'pa':'Punjabi','ro':'Romanian','ru':'Russian','sa':'Sanskrit','sr':'Serbian','sd':'Sindhi','si':'Sinhalese'
		, 'sk':'Slovak','sl':'Slovenian','es':'Spanish','sw':'Swahili','sv':'Swedish','tg':'Tajik','ta':'Tamil','tl':'Tagalog'
		, 'te':'Telugu','th':'Thai','bo':'Tibetan','tr':'Turkish','uk':'Ukrainian','ur':'Urdu','uz':'Uzbek','ug':'Uighur','vi':'Vietnamese'
		}

	if not text:
		return ", ".join(["%s (%s)" %(v, k) for k, v in google_langs.items()])

	text = urllib.quote(text.encode('utf-8'))
	data = misc.readUrl('http://ajax.googleapis.com/ajax/services/language/detect?v=1.0&q=%s' %(text))
	if not data: return 'can\'t get data'

	try:
		convert = loads(data)
		results = convert['responseData']['language']

		return '%s (%s)' %(google_langs[results], results)
	except:
		return 'can\'t detect this shit!'
