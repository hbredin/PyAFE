from lxml import etree
from lxml import objectify
import time
import datetime

# ---- Date/Time range ----

class DateTimeRange (object):
	"""docstring for PYODateTimeRange"""
	def __init__(self, dtStart, dtStop):
		super(DateTimeRange, self).__init__()
		self.dtStart = dtStart
		self.dtStop  = dtStop
	
	def containsDateTime(self, dt):
		#       self starts before dt       and  self stops after dt
		return ((cmp(dt, self.dtStart) >= 0) and (cmp(self.dtStop, dt) >= 0)) 
	
	def containsDateTimeRange(self, dtr):
		#       self starts before dtr               and self stops after dtr
		return ((cmp(dtr.dtStart, self.dtStart) >= 0) and (cmp(self.dtStop, dtr.dtStop) >= 0))
	
	def compareStart(self, dtr):
		return cmp(self.dtStart, dtr.dtStart)

# ---- Yacast Advertisement ----

class YacastAdvertisement(object):
	"""docstring for YacastAdvertisement"""
	def __init__(self, xmlAdvertisement):
		self.media = xmlAdvertisement.idMedia
		self.name  = xmlAdvertisement.name
		self.description = xmlAdvertisement.description
		tStart =  time.strptime(str(xmlAdvertisement.startDate), "%Y-%m-%d %H:%M:%S")
		tEnd =  time.strptime(str(xmlAdvertisement.endDate), "%Y-%m-%d %H:%M:%S")
		dtStart = datetime.datetime(*tStart[0:6])
		dtEnd = datetime.datetime(*tEnd[0:6])
		self.datetimerange = DateTimeRange(dtStart, dtEnd) 
	def compareStart(self, yad):
		return self.datetimerange.compareStart(yad.datetimerange)


def loadYacastAdvertisementList(path2xml):
	obj = objectify.parse(path2xml)
	root = obj.getroot()
	allAds = root.Advertisement

	numAd = len(allAds)
	adsList = []
	for oneAd in allAds:
		adsList.append(YacastAdvertisement(oneAd))

	adsList.sort(YacastAdvertisement.compareStart)
	return adsList	

# ---- Yacast Music ----

class YacastMusic(object):
	"""docstring for YacastMusic"""
	def __init__(self, xmlMusic):
		self.id = xmlMusic.id
		self.title = xmlMusic.title
		self.artist = xmlMusic.artist
		self.label = xmlMusic.label
		self.genre = xmlMusic.genre
		tStart =  time.strptime(str(xmlMusic.startDate), "%Y-%m-%d %H:%M:%S")
		tEnd =  time.strptime(str(xmlMusic.endDate), "%Y-%m-%d %H:%M:%S")
		dtStart = datetime.datetime(*tStart[0:6])
		dtEnd = datetime.datetime(*tEnd[0:6])
		self.datetimerange = DateTimeRange(dtStart, dtEnd) 
		self.filename = xmlMusic.fileName
		self.media = xmlMusic.idMedia
	def compareStart(self, yad):
		return self.datetimerange.compareStart(yad.datetimerange)

def loadYacastMusicList(path2xml):
	obj = objectify.parse(path2xml)
	root = obj.getroot()
	allMusics = root.MusicTrack

	numMusic = len(allMusics)
	musicsList = []
	for oneMusic in allMusics:
		musicsList.append(YacastMusic(oneMusic))

	musicsList.sort(YacastMusic.compareStart)
	return musicsList	

# ---- Participant submission ----





# ---- Main program ----

the_ad_list = loadYacastAdvertisementList("/Users/bredin/Development/Quaero/WP11.4/EvaluationFramework/Advertising.xml")

the_music_list = loadYacastMusicList("/Users/bredin/Development/Quaero/WP11.4/EvaluationFramework/Music.xml")

for the_ad in the_ad_list:
	print the_ad.datetimerange.dtStart.strftime("%Y-%m-%d %H:%M:%S") + " " + the_ad.name
	
for the_music in the_music_list:
	print the_music.datetimerange.dtStart.strftime("%Y-%m-%d %H:%M:%S") + " " + str(the_music.id)


