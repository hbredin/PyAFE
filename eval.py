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


import yacastIO
import submissionIO
import getopt, sys

class eval_result(object):
    """docstring for evaluation"""
    def __init__(self):
        self.participant = ""
        self.submission = ""
        self.number = 0
        self.missed = 0 
        self.good = 0 
        self.bad1 = 0 
        self.hole_bad1 = 0
        self.bad2 = 0
        self.hole_bad2 = 0
        self.bad3 = 0
        self.hole_bad3 = 0
        pass
        
    def show(self):
        """docstring for show"""
        print self.description()
        
    def description(self):
        descr = self.participant + " " + self.submission
        descr = descr + " | P2 = "       + "%+.3f" % (1.0*(self.good-self.bad2-self.hole_bad2)/self.number)
        descr = descr + " | P3 = "       + "%+.3f" % (1.0*(self.good-self.bad3-self.hole_bad3)/self.number)  
        descr = descr + " | P2.5 = "      + "%+.3f" % (1.0*(self.good-self.bad2-self.hole_bad3)/self.number)
        descr = descr + " | Hit = "         + "%4d/%4d" % (self.good, self.number)
        descr = descr + " | Miss = "        + "%4d" % (self.missed)
        descr = descr + " | False Alarm = " + "[%3d+%3d / %3d+%3d / %3d+%3d]" % (self.bad1, self.hole_bad1, self.bad2, self.hole_bad2, self.bad3, self.hole_bad3)       
        return  descr
      
    def add(self, other):
        if (other.participant != None):
            self.participant = other.participant 
        if (other.submission != None):
            self.submission = other.submission
        self.number = self.number + other.number
        self.missed = self.missed + other.missed
        self.good = self.good + other.good
        self.bad1 = self.bad1 + other.bad1
        self.hole_bad1 = self.hole_bad1 + other.hole_bad1
        self.bad2 = self.bad2 + other.bad2
        self.hole_bad2 = self.hole_bad2 + other.hole_bad2
        self.bad3 = self.bad3 + other.bad3
        self.hole_bad3 = self.hole_bad3 + other.hole_bad3
        return self

def eval_events(reference_events, submission_events, skipTwoDaysEvents, fingerprints, verbosity):
    """docstring for eval"""
    
    e = eval_result()
    
    # e.participant = submission.participantId 
    # e.submission = submission.submissionId
    e.number = len(reference_events)
    e.missed = 0 # number of times nothing is detected
    e.good = 0 # number of times correct event is detected (common to all metrics)
    e.bad1 = 0 
    e.hole_bad1 = 0
    e.bad2 = 0
    e.hole_bad2 = 0
    e.bad3 = 0
    e.hole_bad3 = 0

    if len(submission_events) == 0:
        e.missed = e.number
        return e

    # add event with ID = -1 to fill holes
    holes = []
    for i in range(0, len(reference_events)-2):
        prev_event = reference_events[i]
        next_event = reference_events[i+1]
        if (cmp(prev_event.dtEnd, next_event.dtStart) < 0):
            hole = yacastIO.YacastEvent(None)
            hole.dtStart = prev_event.dtEnd
            hole.dtEnd   = next_event.dtStart
            hole.id      = -1
            hole.adjudication = ""
            holes.append(hole)
    
    # add a hole at the beginning if submitted events starts before first reference event
    first_ref_event = reference_events[0]
    first_sub_event = submission_events[0]
    if (cmp(first_sub_event.dtStart, first_ref_event.dtStart) < 0):
        hole = yacastIO.YacastEvent(None)
        hole.dtStart = first_sub_event.dtStart
        hole.dtEnd = first_ref_event.dtStart
        hole.id = -1
        hole.adjudication = ""
        holes.append(hole)
        
    # add a hole at the end if submitted events ends after last reference event
    last_ref_event = reference_events[-1]
    last_sub_event = submission_events[-1]
    if (cmp(last_sub_event.dtEnd, last_ref_event.dtEnd) > 0):
        hole = yacastIO.YacastEvent(None)
        hole.dtStart = last_ref_event.dtEnd
        hole.dtEnd = last_sub_event.dtEnd
        hole.id = -1
        hole.adjudication = ""
        holes.append(hole)
        
    # add holes
    filled_reference_events = []
    filled_reference_events.extend(reference_events)
    filled_reference_events.extend(holes)
    filled_reference_events.sort(yacastIO.YacastEvent.compareDate)

    # for each event in reference
    for cur_event in filled_reference_events:
        
        if cur_event.adjudication == "BAD ANNOTATION":
            if verbosity > 1:
                print cur_event.description() + " ==> BAD ANNOTATION"
            e.number = e.number - 1
            cur_event.id = -1
        
        # if cur_event.adjudication == "DOUBLE ANNOTATION":
        #     if verbosity > 1:
        #         print cur_event.description() + " ==> SKIP (DOUBLE ANNOTATION)"
        #     e.number = e.number - 1
        #     continue
        
        # check if reference event is fully included in one calendar day
        # if it is not and user specifically asked not to evaluate this kind of events, skip it
        if cur_event.isFullyIncludedInOneCalendarDay() == False:
            if skipTwoDaysEvents:
                e.number = e.number - 1 # decrement number of reference events
                if verbosity > 1:
                    print cur_event.description() + " ==> SKIP" # LOG
                continue
        
        # if user asked to focus on a predefined list of fingerprints
        # test if it is available
        if fingerprints != {}:
            if (cur_event.id != -1) and ((cur_event.id in fingerprints.keys()) == False):
                e.number = e.number -1 # decrement number of reference events
                if verbosity > 1:
                    print cur_event.description() + " ==> NO FINGERPRINT (%s)" % (cur_event.id) # LOG
                continue
        
        # array 'inter_events' contains events that are detected during 'cur_event'
        inter_events = cur_event.findIntersectingEvents(submission_events)
        
        # 'missed' is incremented if no event is detected during 'cur_event' 
        if cur_event.id != -1:
            if len(inter_events) == 0:
                e.missed = e.missed + 1
                if verbosity > 1:
                    print cur_event.description() + " ==> MISS (#" + str(cur_event.id) + ")" # LOG

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
            if verbosity > 2:
                print cur_event.description() + " ==> HIT (#" + str(cur_event.id) + ")" # LOG
        
        local_bad1 = 0
        local_hole_bad1 = 0
        local_bad2 = 0
        local_hole_bad2 = 0
        local_bad3 = 0
        local_hole_bad3 = 0

        for cur_id in inter_counter.keys():
            # wrong detection
            if cur_id != cur_event.id:
                if verbosity > 1:
                    if cur_event.id == -1:
                        print cur_event.description() + " ==> FALSE ALARM (#" + str(cur_id) + " INSTEAD OF NO SONG)"
                    else:
                        print cur_event.description() + " ==> FALSE ALARM (#" + str(cur_id) + " INSTEAD OF #" + str(cur_event.id) + ")"# LOG
                
                if cur_event.id == -1:
                    local_hole_bad1 = 1
                    local_hole_bad2 = local_hole_bad2 + 1
                    local_hole_bad3 = local_hole_bad3 + inter_counter[ cur_id ]
                else:
                    # activate error flag
                    local_bad1 = 1
                    # add one error per bad id
                    # (only one error for multiple bad detections with same ad 'id')
                    local_bad2 = local_bad2 + 1
                    # add one error per bad detection
                    # (as many errors as bad detections)
                    local_bad3 = local_bad3 + inter_counter[ cur_id ]

        e.bad1 = e.bad1 + local_bad1
        e.bad2 = e.bad2 + local_bad2
        e.bad3 = e.bad3 + local_bad3
        e.hole_bad1 = e.hole_bad1 + local_hole_bad1
        e.hole_bad2 = e.hole_bad2 + local_hole_bad2
        e.hole_bad3 = e.hole_bad3 + local_hole_bad3

        
    return e
    
def eval_ads(path2xml_ad, path2xml_sub, skipTwoDaysEvents, fingerprints, verbosity):
    """docstring for eval_ads"""
        
    # load reference advertisement XML
    ads = yacastIO.loadAdvertisementList(path2xml_ad)
    # load submission XML
    submission = submissionIO.loadSubmission(path2xml_sub)
 
    # perform ad evaluation
    e = eval_events(ads, submission.ad_list, skipTwoDaysEvents, fingerprints, verbosity)
    
    e.participant = submission.participantId 
    e.submission = submission.submissionId
    
    return e

def eval_zik(path2xml_zik, path2xml_sub, skipTwoDaysEvents, fingerprints, verbosity):
    """docstring for eval_zik"""

    # load reference music XML
    zik = yacastIO.loadMusicList(path2xml_zik)
    # load submission XML
    submission = submissionIO.loadSubmission(path2xml_sub)

    # perform ad evaluation
    e = eval_events(zik, submission.zik_list, skipTwoDaysEvents, fingerprints, verbosity)

    e.participant = submission.participantId 
    e.submission = submission.submissionId

    return e


def usage():
	print "HELP eval_cmd.py :"
	print "  -a, --ads          Advertising XML file"
	print "  -m, --music        Music XML file"
	print "  -s, --submission   Sumission XML file"
	print "  -h, --help         Print this help"

if __name__ == '__main__':
    try:
    	opts, args = getopt.getopt(sys.argv[1:], "ha:m:s:", ["help", "ads=", "music=", "submission="])
    except getopt.GetoptError, err:
    	# print help information and exit:
    	print str(err) # will print something like "option -a not recognized"
    	usage()
    	sys.exit(2)
    path2xml_ad = "";
    path2xml_zik = "";
    path2xml_sub = "";
    # print opts
    # print args
    for opt, arg in opts:
    	if opt in ("-h", "--help"):
    		usage()
    		sys.exit()
    	elif opt in ("-a", "--ads"):
    		path2xml_ad = arg
    	elif opt in ("-m", "--music"):
    		path2xml_zik = arg
    	elif opt in ("-s", "--submission"):
    		path2xml_sub = arg
    	else:
    		assert False, "unhandled option"

    if len(path2xml_sub) == 0:
    	print "Error : no submission file submitted."
    	sys.exit(2)
    if len(path2xml_ad) != 0:
    	ad = eval_ads(path2xml_ad, path2xml_sub, False, 0)
    	print "Advertisement :", 
    	ad.show()
    if len(path2xml_zik) != 0:
    	zik = eval_zik(path2xml_zik, path2xml_sub, False, 0)
    	print "Music :", 
    	zik.show()
    