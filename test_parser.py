import yacastIO
import submissionIO

path2xml_ad  = "/Users/bredin/Development/Quaero/WP11.4/EvaluationFramework/Advertising.xml"
path2xml_zik = "/Users/bredin/Development/Quaero/WP11.4/EvaluationFramework/Music.xml"
path2xml_sub = "/Users/bredin/Development/Quaero/WP11.4/EvaluationFramework/submission.xml"

print "Loading reference Advertisement XML"
ref_ad_list = yacastIO.loadAdvertisementList(path2xml_ad)

print "Loading reference Music XML"
ref_music_list = yacastIO.loadMusicList(path2xml_zik)

print "Loading submission XML"
the_submission = submissionIO.loadSubmission(path2xml_sub)

print the_submission.participantId + " - " + the_submission.submissionId

for the_ad in ref_ad_list:
    
    print the_ad.timerange_description()
    # find all ads in submission that (temporally) intersects the_ad
    the_intersecting_ad_list = the_ad.findIntersectingEvents(the_submission.ad_list)
    print str(len(the_intersecting_ad_list)) + " detections"
    # accumulate found ids
    found_ids = {}
    
    for the_intersecting_ad in the_intersecting_ad_list:
        if the_intersecting_ad.id in found_ids:
            found_ids[ the_intersecting_ad.id ] = found_ids[ the_intersecting_ad.id ] + 1
        else:
            found_ids[ the_intersecting_ad.id ] = 1
    
    count_correct = 0
    count_bad = {}
    for current_id in found_ids.keys():
        if current_id == the_ad.id:
            count_correct = found_ids[ current_id ]
        else:
            count_bad[ current_id ] = found_ids[ current_id ]
            
    