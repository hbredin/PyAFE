import yacastIO
import submissionIO
import datetimerange

the_ad_list = yacastIO.loadAdvertisementList("/Users/bredin/Development/Quaero/WP11.4/EvaluationFramework/Advertising.xml")

the_music_list = yacastIO.loadMusicList("/Users/bredin/Development/Quaero/WP11.4/EvaluationFramework/Music.xml")

for the_ad in the_ad_list:
	print the_ad.datetimerange.dtStart.strftime("%Y-%m-%d %H:%M:%S") + " " + the_ad.name
	
for the_music in the_music_list:
	print the_music.datetimerange.dtStart.strftime("%Y-%m-%d %H:%M:%S") + " " + str(the_music.id)



the_submission = submissionIO.loadSubmission("/Users/bredin/Development/Quaero/WP11.4/EvaluationFramework/submission.xml")
