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

# List of tags than can be used to indicate the event ID
idTags = ['id', 'idMusic', 'idAd']

# Format used by Yacast to store date/time
yacastDateTimeFormat = "%Y-%m-%d %H:%M:%S.%f"

class YacastEvent(object):
    """YacastEvent"""
    
    # Initializer    
    def __init__(self, xmlEvent):
        
        super(YacastEvent, self).__init__()
        
        self.dtStart = None
        self.dtEnd = None
        self.id = None
        self.XML = xmlEvent

        if xmlEvent == None:
            return
        
        # Get start date/time when available
        if hasattr(xmlEvent, 'startDate'):
            self.dtStart = datetime.datetime.strptime(str(xmlEvent.startDate), yacastDateTimeFormat)
        # Get end date/time when available
        if hasattr(xmlEvent, 'endDate'):
            self.dtEnd = datetime.datetime.strptime(str(xmlEvent.endDate), yacastDateTimeFormat)
            
        # Get event date/time when one of start/stop date is missing
        if self.dtStart == None or self.dtEnd == None:
            if hasattr(xmlEvent, 'eventDate'):
                self.dtStart = datetime.datetime.strptime(str(xmlEvent.eventDate), yacastDateTimeFormat)
                self.dtEnd = datetime.datetime.strptime(str(xmlEvent.eventDate), yacastDateTimeFormat)
                
        for element in xmlEvent.iterchildren():
            if element.tag in idTags:
                self.id = str(element)
        
                    
    def compareByDate(self, other):
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

def fillTimelineWithDummyEvent(eventList, dtStart, dtEnd, dummyID):
    """fillTimelineWithDummyEvent"""
    
    dummies = []
    
    # Add a dummy event at the beginning
    if cmp(dtStart, eventList[0].dtStart) < 0:
        dummy = YacastEvent(None)
        dummy.dtStart = dtStart
        dummy.dtEnd   = eventList[0].dtStart
        dummy.id      = dummyID
        dummies.append(dummy)
        
    # Add a dummy event at the end
    if cmp(eventList[-1].dtEnd, dtEnd) < 0:
        dummy = YacastEvent(None)
        dummy.dtStart = eventList[-1].dtEnd
        dummy.dtEnd   = dtEnd
        dummy.id      = dummyID
        dummies.append(dummy)
        
    # Fill holes with dummy events
    for i in range(1, len(eventList)):
        leftEvent  = eventList[i-1]
        rightEvent = eventList[i]
        if cmp(leftEvent.dtEnd, rightEvent.dtStart) < 0:
            dummy = YacastEvent(None)
            dummy.dtStart = leftEvent.dtEnd
            dummy.dtEnd   = rightEvent.dtStart
            dummy.id      = dummyID
            dummies.append(dummy)
    
    modifiedEventList = []
    for e in eventList:
        modifiedEventList.append(e)
    for d in dummies:
        modifiedEventList.append(d)
    modifiedEventList.sort(YacastEvent.compareByDate)
    
    return modifiedEventList

class YacastAnnotations(object):
    """YacastAnnotations"""
    def __init__(self, path2xml):
        super(YacastAnnotations, self).__init__()
        
        self.eventList = {}
        
        if path2xml == None:
            return self
        
        xmlroot = objectify.parse(path2xml).getroot()
        if xmlroot == None:
            return self
                
        # Loop on all elements in detection list
        for element in xmlroot.iterchildren():
            # Get type of elements (e.g <MusicTrack> or <Advertisement>)
            eventType = element.tag
            # Creates new entry in dictionary if necessary
            if eventType not in self.eventList.keys():
                self.eventList[eventType] = []
            # Add element to the list of elements of this type
            self.eventList[eventType].append(YacastEvent(element))
        for eventType in self.eventList.keys():
            self.eventList[eventType].sort(YacastEvent.compareByDate)
        
