import xbmcaddon, xbmcgui,xbmcplugin		# for xbmc interaface
import mechanize, urllib, json				# for web
from BeautifulSoup import BeautifulSoup		# parsing responses

# XBMC plugin for http://stream.mv
# 2013 - @kudanai
# released under GNU GPL v3.0

__settings__ = xbmcaddon.Addon()
__author__   = __settings__.getAddonInfo("author")
__scriptid__ = __settings__.getAddonInfo("id")
__cwd__      = __settings__.getAddonInfo("path")


def add_urls(streamURLS):
	"""
	add links to the xbmc interface
	"""
	if not streamURLS:
		exit() #todo: figure out how to raise an error

	#iterate through the URLS and add links
	for channel in streamURLS.keys():
		iconimage=streamURLS[channel]["img"]
		li = xbmcgui.ListItem(unicode(channel),iconImage=iconimage,thumbnailImage=iconimage)
		li.setInfo( type="Video", infoLabels={ "Title": channel})
		ok=xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=streamURLS[channel]["url"],listitem=li,isFolder=False)

	return ok


def get_stream_urls(USERNAME,PASSWORD):
	"""
	rip out the streamURLS from the website
	must return a playlist dict
	"""

	#init mechanize object
	br=mechanize.Browser()
	br.set_handle_robots(False) # ignore robots
	br.addheaders = [('User-agent', 'Mozilla/5.0 (iPhone; CPU iPhone OS 5_0 like Mac OS X) AppleWebKit/534.46 (KHTML, like Gecko) Version/5.1 Mobile/9A334 Safari/7534.48.3')]
	
	response = br.open(
		"http://stream.mv/ajax.php",
		urllib.urlencode({'email':USERNAME,
			'password':PASSWORD,
			'todo':'login'}
			)
		)

	loginresponse = json.loads(response.read())

	if not loginresponse['empty_login']: #empty_login has a url if it's valid
		settings = xbmcaddon.Addon(id='plugin.video.mvstream').openSettings()

	br.open(loginresponse['empty_login'])
	return parse_response(br)


def parse_response(browser):
	"""
	extract the urls and stuff
	"""

	soup = BeautifulSoup(browser.response().read())

	#this will be ui dependant
	streamURLS={}
	f = soup.find('ul',id='selectList')
	for link  in f.findAll('li'):
		url=link.find('a').get('href');
		img=link.find('img').get('data-cfsrc')
		title=link.getText()
		if url != '#':
			streamURLS[title]={
				'url':get_video_url(browser,url),
				'img':img
			}

	
	return streamURLS


def get_video_url(browser,url):
	"""
	visit page with video player and extract the thing
	"""
	soup=BeautifulSoup(browser.open(url).read())
	return soup.source.get('src')


if __name__ == '__main__':
	"""entry point"""

	username = __settings__.getSetting("username")
	password = __settings__.getSetting("password")

	if not username or not password:
		__settings__.openSettings()
	else:
		urls=get_stream_urls(username,password)
		add_urls(urls)
	
	xbmcplugin.endOfDirectory(int(sys.argv[1]))