from lxml import etree
from lxml import objectify
import time
import datetime
import yacastIO

class Submission(object):
    """docstring for Submission"""
    def __init__(self, xmlroot):
        super(Submission, self).__init__()
        
        if xmlroot == None:
            self.submissionId = None
            self.participantId = None
            self.ad_list = []
            self.zik_list = []
        else:
            if hasattr(xmlroot, 'submissionId'):
                self.submissionId = xmlroot.submissionId
            if hasattr(xmlroot, 'participantId'):
                self.participantId = xmlroot.participantId

            if hasattr(xmlroot, 'detectionList'):
                if hasattr(xmlroot.detectionList, 'Advertisement'):
                    all_ad = xmlroot.detectionList[0].Advertisement
                else:
                    all_ad = []
                if hasattr(xmlroot.detectionList, 'MusicTrack'):
                    all_zik = xmlroot.detectionList[0].MusicTrack
                else:
                    all_zik = []
        
            self.ad_list = []
            for one_ad in all_ad:
                self.ad_list.append(yacastIO.YacastAd(one_ad))
            self.ad_list.sort(yacastIO.YacastEvent.compareDate)

            self.zik_list = []
            for one_zik in all_zik:
                self.zik_list.append(yacastIO.YacastZik(one_zik))
            self.zik_list.sort(yacastIO.YacastZik.compareDate)


def loadSubmission(path2xml):
    if path2xml == None:
        return Submission(None)
    else:
        obj = objectify.parse(path2xml)
        root = obj.getroot()
        return Submission(root)

