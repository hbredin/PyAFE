from lxml import etree
from lxml import objectify
import time
import datetime
import datetimerange

# ---- Yacast Advertisement ----
class YacastAdvertisement(object):
    """docstring for YacastAdvertisement"""
    def __init__(self, xmlAdvertisement):
        self.media = xmlAdvertisement.idMedia
        if hasattr(xmlAdvertisement, 'name'):
            self.name  = xmlAdvertisement.name
        if hasattr(xmlAdvertisement, 'description'):
            self.description = xmlAdvertisement.description
        tStart = time.strptime(str(xmlAdvertisement.startDate), "%Y-%m-%d %H:%M:%S")
        tEnd =  time.strptime(str(xmlAdvertisement.endDate), "%Y-%m-%d %H:%M:%S")
        dtStart = datetime.datetime(*tStart[0:6])
        dtEnd = datetime.datetime(*tEnd[0:6])
        self.datetimerange = datetimerange.DateTimeRange(dtStart, dtEnd) 
    
    def compareStart(self, yad):
        return self.datetimerange.compareStart(yad.datetimerange)

# ---- Yacast Music ----
class YacastMusic(object):
    """docstring for YacastMusic"""
    def __init__(self, xmlMusic):
        if hasattr(xmlMusic, 'id'):
            self.id = xmlMusic.id
        if hasattr(xmlMusic, 'title'):
            self.title = xmlMusic.title
        if hasattr(xmlMusic, 'artist'):
            self.artist = xmlMusic.artist
        if hasattr(xmlMusic, 'label'):
            self.label = xmlMusic.label
        if hasattr(xmlMusic, 'genre'):
            self.genre = xmlMusic.genre
        tStart =  time.strptime(str(xmlMusic.startDate), "%Y-%m-%d %H:%M:%S")
        tEnd =  time.strptime(str(xmlMusic.endDate), "%Y-%m-%d %H:%M:%S")
        dtStart = datetime.datetime(*tStart[0:6])
        dtEnd = datetime.datetime(*tEnd[0:6])
        self.datetimerange = datetimerange.DateTimeRange(dtStart, dtEnd) 
        if hasattr(xmlMusic, 'fileName'):
            self.filename = xmlMusic.fileName
        if hasattr(xmlMusic, 'idMedia'):
            self.media = xmlMusic.idMedia
    
    def compareStart(self, yad):
        return self.datetimerange.compareStart(yad.datetimerange)

# --- Load Yacast Advertising.xml files as array of YacastAdvertisement
def loadAdvertisementList(path2xml):
    obj = objectify.parse(path2xml)
    root = obj.getroot()
    allAds = root.Advertisement

    numAd = len(allAds)
    adsList = []
    for oneAd in allAds:
        adsList.append(YacastAdvertisement(oneAd))

    adsList.sort(YacastAdvertisement.compareStart)
    return adsList    

# --- Load Yacast Music.xml files as array of YacastMusic
def loadMusicList(path2xml):
    obj = objectify.parse(path2xml)
    root = obj.getroot()
    allMusics = root.MusicTrack

    numMusic = len(allMusics)
    musicsList = []
    for oneMusic in allMusics:
        musicsList.append(YacastMusic(oneMusic))

    musicsList.sort(YacastMusic.compareStart)
    return musicsList    
