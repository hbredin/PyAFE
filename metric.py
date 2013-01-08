# Copyright 2010 Herve BREDIN (bredin@limsi.fr) and Mathieu RAMONA (Mathieu.Ramona@ircam.fr)
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


import getopt, sys

from yacastIO import *
import submissionIO

PyAFE_fillerID = "PyAFE_No_Track"

class Metric(object):
    """Metric"""
    def __init__(self):
        
        self.number = 0
        self.missed = 0
        self.good = 0
        
        self.fa2 = 0           # Score 2
        self.fa2_out = 0
        
        self.fa1 = 0           # Score 1
        self.fa1_out = 0
                
    def description(self):
        descr = ""
        descr = descr +    "Hit (Miss) / Total => %d (%d) / %d" % (self.good, self.missed, self.number)
        descr = descr + " | FA1 (out) = %d (%d) | FA2 (out) = %d (%d)" % (self.fa2, self.fa2_out, self.fa1, self.fa1_out)       
        descr = descr + " | R1 = %+.3f" % (1.0*(self.good-self.fa1-self.fa1_out)/self.number)  
        descr = descr + " | R2 = %+.3f" % (1.0*(self.good-self.fa2-self.fa2_out)/self.number)
        descr = descr + " | R1.5 = %+.3f" % (1.0*(self.good-self.fa2-self.fa1_out)/self.number)
        return  descr
      
    def add(self, other):
        self.number = self.number + other.number
        self.missed = self.missed + other.missed
        self.good = self.good + other.good
        self.fa2 = self.fa2 + other.fa2
        self.fa2_out = self.fa2_out + other.fa2_out
        self.fa1 = self.fa1 + other.fa1
        self.fa1_out = self.fa1_out + other.fa1_out
        return self

def compute_metric(reference_events, submission_events, options):
    """compute_metric"""
    
    e = Metric()

    if options.limitedhours:
        dtStart = reference_events[0].dtStart.replace(hour=options.startH, minute=options.startM, second=options.startS, microsecond=0)
        dtEnd = reference_events[-1].dtEnd.replace(hour=options.endH, minute=options.endM, second=options.endS, microsecond=99999)
    else:
        dtStart = reference_events[0].dtStart.replace(hour=0, minute=0, second=0, microsecond=0)
        dtEnd = reference_events[-1].dtEnd.replace(hour=23, minute=59, second=59, microsecond=99999)

    # Check that dtStart < dtEnd in TimeSlot.txt (useful if -l option is provided)
    if options.limitedhours and cmp(dtStart,dtEnd) > 0:
        print "%s > ERROR - Start time should be before End time" % (options.path2xml_ts)
        return None

    # Check that reference_events[0].dtStart < option.dtStart < reference_events[-1].dtEnd
    if options.limitedhours and ((cmp(dtStart, reference_events[0].dtStart) < 0) or (cmp(dtStart, reference_events[-1].dtEnd) > 0)):
        print "%s > ERROR - Start time should be between reference start (%s) and reference end (%s)" % (options.path2xml_ts,str(reference_events[0].dtStart),str(reference_events[-1].dtEnd))
        return None

    # Check that reference_events[0].dtStart < option.dtEnd < reference_events[-1].dtEnd
    if options.limitedhours and ((cmp(dtEnd, reference_events[0].dtStart) < 0) or (cmp(dtEnd, reference_events[-1].dtEnd) > 0)): 
        print "%s > ERROR - End time should be between reference start (%s) and reference end (%s)" % (options.path2xml_ts,reference_events[0].dtStart.strftime('%H:%M:%S'),reference_events[-1].dtEnd.strftime('%H:%M:%S'))
        return None

    filled_reference_events = fillTimelineWithDummyEvent(reference_events, dtStart, dtEnd, PyAFE_fillerID)

    # Total number of events to be detected
    e.number = len(reference_events)
    
    e.missed = 0 # number of times nothing is detected
    e.good = 0 # number of times correct event is detected (common to all metrics)
    e.fa2 = 0
    e.fa2_out = 0
    e.fa1 = 0
    e.fa1_out = 0
    
    # for each event in reference
    for cur_event in filled_reference_events:
        # if event is annotated 'skip'
        if cur_event.skip:
            e.number = e.number - 1 # decrement number of reference events
            if options.verbosity > 1:
                print cur_event.description() + " ==> SKIP #" + str(cur_event.id) # LOG
            continue

        # check if reference event is fully included in one calendar day
        # if it is not and user specifically asked not to evaluate this kind of events, skip it
        if cur_event.id != PyAFE_fillerID and cur_event.isFullyIncludedInOneCalendarDay() == False and options.skipTwoDaysEvents:
            e.number = e.number - 1 # decrement number of reference events
            if options.verbosity > 1:
                print cur_event.description() + " ==> SKIP (2-DAYS EVENT)" # LOG
            continue
        
        # if user asked to focus on a predefined list of fingerprints
        # test if it is available
        if options.fingerprints != {}:
            if (cur_event.id != PyAFE_fillerID) and ((cur_event.id in options.fingerprints.keys()) == False):
                e.number = e.number - 1 # decrement number of reference events
                if options.verbosity > 1:
                    print cur_event.description() + " ==> UNKNOWN FINGERPRINT #" + str(cur_event.id) # LOG
                continue
        
        # array 'inter_events' contains events that are detected during 'cur_event'
        inter_events = cur_event.findIntersectingEvents(submission_events)
        
        # 'missed' is incremented if no event is detected during 'cur_event' 
        if cur_event.id != PyAFE_fillerID:
            if len(inter_events) == 0:
                e.missed = e.missed + 1
                if options.verbosity > 1:
                    print cur_event.description() + " ==> MISSED DETECTION #" + str(cur_event.id) # LOG

        # 'inter_counter[id]' is the number of time event with index 'id' is detected during 'cur_event'
        inter_counter = {} 
        
        for cur_inter_event in inter_events:
            #  increment counter for detected event with index 'id'
            if cur_inter_event.id in inter_counter.keys():
                inter_counter[ cur_inter_event.id ] = inter_counter[ cur_inter_event.id ] + 1
            else:
                inter_counter[ cur_inter_event.id ] = 1
        
        # is 'cur_event' correctly detected?
        if cur_event.id in inter_counter.keys():
            e.good = e.good + 1
            if options.verbosity > 2:
                print cur_event.description() + " ==> HIT (#" + str(cur_event.id) + ")" # LOG

        # 'missed' is also incremented if some events are detected during 'cur_event', but not the right one
        # Nothing is printed, it corresponds to the case "FALSE ALARM (# X INSTEAD OF # cur_event)"
        if (cur_event.id not in inter_counter.keys()) and (len(inter_events) > 0) and (cur_event.id != PyAFE_fillerID):
            e.missed = e.missed + 1       

        local_fa2 = 0
        local_fa2_out = 0
        local_fa1 = 0
        local_fa1_out = 0

        for cur_id in inter_counter.keys():
            # wrong detection
            if cur_id != cur_event.id:
                if options.verbosity > 1:
                    if cur_event.id == PyAFE_fillerID:
                        print cur_event.description() + " ==> FALSE ALARM (#" + str(cur_id) + " INSTEAD OF NO SONG)"
                    else:
                        print cur_event.description() + " ==> FALSE ALARM (#" + str(cur_id) + " INSTEAD OF #" + str(cur_event.id) + ")"# LOG
                
                if cur_event.id == PyAFE_fillerID:
                    local_fa2_out = local_fa2_out + 1
                    local_fa1_out = local_fa1_out + inter_counter[ cur_id ]
                else:
                    # add one error per bad id
                    # (only one error for multiple bad detections with same ad 'id')
                    local_fa2 = local_fa2 + 1
                    # add one error per bad detection
                    # (as many errors as bad detections)
                    local_fa1 = local_fa1 + inter_counter[ cur_id ]

        e.fa2 = e.fa2 + local_fa2
        e.fa1 = e.fa1 + local_fa1
        e.fa2_out = e.fa2_out + local_fa2_out
        e.fa1_out = e.fa1_out + local_fa1_out
    
    return e
    
