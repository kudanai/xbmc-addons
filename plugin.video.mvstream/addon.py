import xbmc, xbmcaddon, xbmcgui,xbmcplugin
import mechanize
import urllib
import json
from BeautifulSoup import BeautifulSoup

# XBMC plugin for http://stream.mv
# 2013 - @kudanai

def Notify(title,message,times,icon):
	"""post a notificiation to the xbmc interface"""
        xbmc.executebuiltin("XBMC.Notification("+title+","+message+","+times+","+icon+")")


def addURLS(streamURLS):
	if not streamURLS:
		exit() #todo: figure out how to raise an error

	#iterate through the URLS and add links
	for channel in streamURLS.keys():
		li = xbmcgui.ListItem(unicode(channel))
		li.setInfo( type="Video", infoLabels={ "Title": channel })
		ok=xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=streamURLS[channel],listitem=li,isFolder=False)

	return ok

def LOGIN(USERNAME,PASSWORD):
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

	soup=BeautifulSoup(br.open(loginresponse['empty_login']).read())

	#this will be ui dependant
	streamURLS={}
	f = soup.find('ul',id='selectList')
	for link  in f.findAll('li'):
		url=link.find('a').get('href');
		title=link.getText()
		if url != '#':
			streamURLS[title]=getStreamURL(br,url);
	
	return streamURLS
	#pass


def getStreamURL(br,url):
	"""
	visit page with video player and extract the thing
	"""
	soup=BeautifulSoup(br.open(url).read())
	return soup.source.get('src')


def INIT():
	settings = xbmcaddon.Addon(id='plugin.video.mvstream')
	username = settings.getSetting("username")
	password = settings.getSetting("password")

	if not username or not password:
		settings.openSettings()
	else:
		streamURLS=LOGIN(username,password)
		addURLS(streamURLS)

INIT()
xbmcplugin.endOfDirectory(int(sys.argv[1]))