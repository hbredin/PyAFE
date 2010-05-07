from lxml import etree
from lxml import objectify
import time
import datetime
import datetimerange
import yacastIO

class Submission(object):
    """docstring for Submission"""
    def __init__(self, xmlroot):
        super(Submission, self).__init__()
        self.submissionId = xmlroot.submissionId
        self.participantId = xmlroot.participantId
 
        all_ad = xmlroot.detectionList[0].Advertisement
        self.ad_list = []
        for one_ad in all_ad:
    		self.ad_list.append(yacastIO.YacastAdvertisement(one_ad))
    	self.ad_list.sort(yacastIO.YacastAdvertisement.compareStart)

        all_music = xmlroot.detectionList[0].MusicTrack
        self.music_list = []
        for one_music in all_music:
    		self.music_list.append(yacastIO.YacastMusic(one_music))
    	self.music_list.sort(yacastIO.YacastMusic.compareStart)


def loadSubmission(path2xml):
    obj = objectify.parse(path2xml)
    root = obj.getroot()
    return Submission(root)

