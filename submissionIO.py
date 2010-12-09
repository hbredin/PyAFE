# Copyright 2010 Herve BREDIN (bredin@limsi.fr)
# Contact: http://pyafe.niderb.fr/

# This file is part of PyAFE.
# 
#     PyAFE is free software: you can redistribute it and/or modify
#     it under the terms of the GNU General Public License as published by
#     the Free Software Foundation, either version 3 of the License, or
#     (at your option) any later version.
# 
#     PyAFE is distributed in the hope that it will be useful,
#     but WITHOUT ANY WARRANTY; without even the implied warranty of
#     MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#     GNU General Public License for more details.
# 
#     You should have received a copy of the GNU General Public License
#     along with PyAFE.  If not, see <http://www.gnu.org/licenses/>.


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

