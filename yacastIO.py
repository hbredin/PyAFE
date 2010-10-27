from lxml import etree
from lxml import objectify
import time
import datetime

class YacastEvent(object):
    """docstring for YacastEvent"""
    
    # Initializer    
    def __init__(self, xmlEvent):
        super(YacastEvent, self).__init__()
        
        if xmlEvent != None:
            # Get start date/time when available
            if hasattr(xmlEvent, 'startDate'):
                tStart = time.strptime(str(xmlEvent.startDate), "%Y-%m-%d %H:%M:%S")
                self.dtStart = datetime.datetime(*tStart[0:6])
        
            # Get end date/time when available
            if hasattr(xmlEvent, 'endDate'):
                tEnd = time.strptime(str(xmlEvent.endDate), "%Y-%m-%d %H:%M:%S")
                self.dtEnd = datetime.datetime(*tEnd[0:6])
        
            # Get event date/time only when start and stop date are not both available
            if not(hasattr(self, 'dtStart')) or not(hasattr(self, 'dtStop')):
                if hasattr(xmlEvent, 'eventDate'):
                    tEvent = time.strptime(str(xmlEvent.eventDate), "%Y-%m-%d %H:%M:%S")
                    self.dtStart = datetime.datetime(*tEvent[0:6])
                    self.dtEnd = datetime.datetime(*tEvent[0:6])
        
            # Get adjudication error when available
            if hasattr(xmlEvent, 'error'):
                self.adjudication = xmlEvent.error
            else:
                self.adjudication = ""
    
    def timerange_description(self):
        """docstring for description"""
        return self.dtStart.strftime("%H:%M:%S") + " - " + self.dtEnd.strftime("%H:%M:%S")
        
    def compareDate(self, other):
        return cmp(self.dtStart, other.dtStart)
    
    def intersects(self, other):
        """returns FALSE if intersection is empty, TRUE otherwise"""
        """see doc/intersection.png for detail"""
        """self = groundtruth / other = detected event"""        
        if (cmp(other.dtStart, other.dtEnd) == 0):
            fullyHappensAfterOther = (cmp(self.dtStart, other.dtStart) > 0)
            happensBeforeOther = (cmp(self.dtEnd, other.dtStart) <= 0)
            if fullyHappensAfterOther or happensBeforeOther:
                return False
            else:
                return True 
        else:
            startsBeforeOtherStarts = (cmp(self.dtStart, other.dtStart) <= 0)    # does self starts before other starts?
            endsAfterOtherStarts = (cmp(self.dtEnd, other.dtStart) >= 0)         # does self ends before other starts?
            startsStrictlyBeforeOtherEnds = (cmp(self.dtStart, other.dtEnd) < 0) # does self starts strictly before other ends?
            if startsBeforeOtherStarts:
                return endsAfterOtherStarts
            else:
                return startsStrictlyBeforeOtherEnds

    def isFullyIncludedInOneCalendarDay(self):
        """returns FALSE if event is not fully included in one calendar day"""
        return self.dtStart.day == self.dtEnd.day

    def findIntersectingEvents(self, sorted_event_list):
        """docstring for findIntersectingEvents"""
        intersecting_events_list = []
        for the_event in sorted_event_list:
            if self.intersects(the_event):
                intersecting_events_list.append(the_event)
        return intersecting_events_list
    
    def description(self):
        return str(self.dtStart) + " > " + str(self.dtEnd) 
        

# Yacast Advertisement
class YacastAd(YacastEvent):
    """docstring for YacastAd"""
    def __init__(self, xmlAdvertisement):
        
        # self = YacastEvent(xmlAdvertisement)
        super(YacastAd, self).__init__(xmlAdvertisement)
        
        if hasattr(xmlAdvertisement, 'id'):
            self.id = str(xmlAdvertisement.id)
        if hasattr(xmlAdvertisement, 'idAd'):
            self.id = str(xmlAdvertisement.idAd)        
        if hasattr(xmlAdvertisement, 'idMedia'):
            self.idMedia = xmlAdvertisement.idMedia
        if hasattr(xmlAdvertisement, 'name'):
            self.name = xmlAdvertisement.name
        if hasattr(xmlAdvertisement, 'brand'):
            self.brand = xmlAdvertisement.brand
        if hasattr(xmlAdvertisement, 'advertiser'):
            self.advertiser = xmlAdvertisement.advertiser
        if hasattr(xmlAdvertisement, 'description'):
            self.description = xmlAdvertisement.description
        if hasattr(xmlAdvertisement, 'signatureFile'):
            self.signatureFile = xmlAdvertisement.signatureFile
    
# Yacast MusicTrack
class YacastZik(YacastEvent):
    """docstring for YacastZik"""
    def __init__(self, xmlMusic):
        
        # self = YacastEvent(xmlMusic)
        super(YacastZik, self).__init__(xmlMusic)
        
        if hasattr(xmlMusic, 'id'):
            self.id = str(xmlMusic.id)
        if hasattr(xmlMusic, 'idMusic'):
            self.id = str(xmlMusic.idMusic)        
        if hasattr(xmlMusic, 'title'):
            self.title = xmlMusic.title
        if hasattr(xmlMusic, 'artist'):
            self.artist = xmlMusic.artist
        if hasattr(xmlMusic, 'label'):
            self.label = xmlMusic.label
        if hasattr(xmlMusic, 'genre'):
            self.genre = xmlMusic.genre
        if hasattr(xmlMusic, 'fileName'):
            self.fileName = xmlMusic.fileName
        if hasattr(xmlMusic, 'signaturePath'):
            self.signaturePath = xmlMusic.signaturePath
        if hasattr(xmlMusic, 'idMedia'):
             self.idMedia = xmlMusic.idMedia


# --- Load Yacast Advertising.xml files as array of YacastAd
def loadAdvertisementList(path2xml):
    obj = objectify.parse(path2xml)
    root = obj.getroot()
    if hasattr( root, 'Advertisement'):
        allAds = root.Advertisement
    else:
        allAds = []
    
    numAd = len(allAds)
    adsList = []
    for oneAd in allAds:
        adsList.append(YacastAd(oneAd))
    
    adsList.sort(YacastEvent.compareDate)
    return adsList

# --- Load Yacast Music.xml files as array of YacastZik
def loadMusicList(path2xml):
    obj = objectify.parse(path2xml)
    root = obj.getroot()
    if hasattr(root, 'MusicTrack'):
        allMusics = root.MusicTrack
    else:
        allMusics = []    
    
    numMusic = len(allMusics)
    musicsList = []
    for oneMusic in allMusics:
        musicsList.append(YacastZik(oneMusic))
    
    musicsList.sort(YacastEvent.compareDate)
    return musicsList    
