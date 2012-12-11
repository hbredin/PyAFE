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
from yacastIO import *
import re


class Submission(object):
    """docstring for Submission"""    
    def __init__(self, path2xml):
        
        super(Submission, self).__init__()

        self.ID = None
        self.participant = None
        self.detectionList = {}

        if path2xml == None:
            return self
        
        idMedia = None
        m = re.search('\d\d\d\d/\d\d/\d\d/(\d+)/.*\.xml', path2xml)
        if m:
            idMedia = m.group(1)

        xmlroot = objectify.parse(path2xml).getroot()
        if xmlroot == None:
            return self
        
        # Read submission identifier from XML file
        if hasattr(xmlroot, 'submissionId'):
            self.ID = xmlroot.submissionId
        
        # Read participant identifier from XML file
        if hasattr(xmlroot, 'participantId'):
            self.participant = xmlroot.participantId
        
        # Read list of detected events 
        if hasattr(xmlroot, 'detectionList'):
            # Loop on all elements in detection list
            for element in xmlroot.detectionList.iterchildren():
                # Get type of elements (e.g <MusicTrack> or <Advertisement>)
                eventType = element.tag
                # Creates new entry in dictionary if necessary
                if eventType not in self.detectionList.keys():
                    self.detectionList[eventType] = []
                # Add element to the list of elements of this type
                event = YacastEvent(element)
                if not hasattr(event,'idMedia') or idMedia == None or event.idMedia == idMedia:
                    self.detectionList[eventType].append(event)
            # Sort 
            for eventType in self.detectionList.keys():
                self.detectionList[eventType].sort(YacastEvent.compareByDate)
