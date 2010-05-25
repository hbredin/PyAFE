# Code by Herve BREDIN (bredin@irit.fr) and Mathieu RAMONA (Mathieu.Ramona@ircam.fr)

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
        self.bad2 = 0
        self.bad3 = 0
        pass
        
    def show(self):
        """docstring for show"""
        print self.participant + " " + self.submission + " | OK = " + str(self.good)  + " | Bad = " + str(self.bad1) + " - " + str(self.bad2) + " - " + str(self.bad3) + " | Missed = " + str(self.missed) + " | Total = " + str(self.number)
        

def eval_events(reference_events, submission_events):
    """docstring for eval"""
    
    e = eval_result()
    
    # e.participant = submission.participantId 
    # e.submission = submission.submissionId
    e.number = len(reference_events)
    e.missed = 0 # number of times nothing is detected
    e.good = 0 # number of times correct event is detected (common to all metrics)
    e.bad1 = 0 # number of bad detection (multiple bad detections for )
    e.bad2 = 0
    e.bad3 = 0

    # for each event in reference
    for cur_event in reference_events:
        
        # array 'inter_events' contains events that are detected during 'cur_event'
        inter_events = cur_event.findIntersectingEvents(submission_events)
        
        # 'missed' is incremented if no event is detected during 'cur_event' 
        if len(inter_events) == 0:
            e.missed = e.missed + 1

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
        
        local_bad1 = 0
        local_bad2 = 0
        local_bad3 = 0

        for cur_id in inter_counter.keys():
            # wrong detection
            if cur_id != cur_event.id:
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
        
    return e
    
def eval_ads(path2xml_ad, path2xml_sub):
    """docstring for eval_ads"""
        
    # load reference advertisement XML
    ads = yacastIO.loadAdvertisementList(path2xml_ad)
    # load submission XML
    submission = submissionIO.loadSubmission(path2xml_sub)
 
    # perform ad evaluation
    e = eval_events(ads, submission.ad_list)
    
    e.participant = submission.participantId 
    e.submission = submission.submissionId
    
    return e

def eval_zik(path2xml_zik, path2xml_sub):
    """docstring for eval_zik"""

    # load reference music XML
    zik = yacastIO.loadMusicList(path2xml_zik)
    # load submission XML
    submission = submissionIO.loadSubmission(path2xml_sub)

    # perform ad evaluation
    e = eval_events(zik, submission.zik_list)

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
    	ad = eval_ads(path2xml_ad, path2xml_sub)
    	print "Advertisement :", 
    	ad.show()
    if len(path2xml_zik) != 0:
    	zik = eval_zik(path2xml_zik, path2xml_sub)
    	print "Music :", 
    	zik.show()
    