import mechanize
import os
import datetime
from BeautifulSoup import BeautifulSoup
import xbmc, xbmcaddon, xbmcgui,xbmcplugin
import threading

#action-codes
ACTION_PREVIOUS_MENU = 10

#GLOBAL VARS
URLs = {
	'home':"http://dportal.dhivehinet.net.mv/",
	'graph':'http://dportal.dhivehinet.net.mv/comparision_graph.php',
	'graph_local':'special://temp/adsl_graph.png'
}

class worker(threading.Thread):
	def __init__(self):
		threading.Thread.__init__(self)
		self.details=None

	def run(self):
		details=get_adsl_usage()
		self.details=details

class displayWindow(xbmcgui.Window):
	"""display window to display the stuff
	waits for setStuff to receive details to render. MUST
	call setStuff before doModal or show"""


	def __init__(self):
		self.x=200;
		self.y=200

		self.setBackground()
		self.setCoordinateResolution(0)

		t=worker()
		t.start()
		t.join()
		self.setStuff(t.details)

	def setBackground(self):
		#add background
		ipath=os.path.dirname(os.path.realpath(__file__))+"/background.jpg"
		self.addControl(xbmcgui.ControlImage(0,0,1920,1080, ipath))

 	def setStuff(self,details):

 		for key in details.keys():

 			#create control
 			label=xbmcgui.ControlLabel(self.x, self.y, 400, 200, '', 'font13', '0xFFFFFFFF')
 			det=xbmcgui.ControlLabel(self.x+400, self.y, 400, 200, '', 'font13', '0xFFFFFF99')
 			
 			#set text
 			label.setLabel(key)
 			det.setLabel(details[key])

 			#add to the gui
 			self.addControl(label)
 			self.addControl(det)

 			#increment x
 			self.y+=40

		#add graph
		self.addControl(xbmcgui.ControlImage(self.x,self.y+100,800,400, xbmc.translatePath(URLs['graph_local'])))

	def onAction(self, action):
		self.close()
 

def get_adsl_usage():
	"""login to the website using the username,
	and password provided"""

	settings = xbmcaddon.Addon(id='script.dhiraaguadsl')
	username = settings.getSetting("username")
	password = settings.getSetting("password")

	#init browser
	br = mechanize.Browser()

	#retrieve the page
	br.open(URLs["home"])
	br.select_form("aspnetForm")

	#set the values & submit
	br.form["web_user"]=username
	br.form["web_pass"]=password

	#submit form
	response = br.submit()

	#download graph
	br.retrieve(URLs["graph"],xbmc.translatePath(URLs['graph_local']))

	#parse details
	details = parse_details(br,response)

	#return details
	return details


def parse_details(browser,response):
	"""read the response object, and extract
	the customer details, download the graph"""

	soup = BeautifulSoup(response.read())

	details={"Date":datetime.date.today().isoformat()}
	for det in  soup.findAll('span','custdet'):
		detail=det.find('div','servdet_subh').getText().strip()
		value=det.find('div','servdet_val').getText().strip()
		details[detail]=value

	return details


def run_first():
	"""invoked on first run,
	gets the settings object and details thereof.
	if settings are not initialized, show the settings menu."""

	settings = xbmcaddon.Addon(id='script.dhiraaguadsl')
	username = settings.getSetting("username")
	password = settings.getSetting("password")

	if not username or not password:
		settings.openSettings()
	else:
		display=displayWindow()
		display.doModal()
		print "returned here"
		del display


# if __name__ == '__main__':
run_first()