import os
import sys
import getopt
import eval

def getListOfRelativePathToFile( mydir, filename ):
    fileList = []
    rootdir = os.path.normpath(mydir)
    for root, subFolders, files in os.walk(rootdir):
        for file in files:
            if file == filename:
                fileList.append(os.path.dirname(os.path.relpath(os.path.join(root,file), rootdir)))
    return fileList


def full_eval_zik(path2groundtruth, path2submission, subname, partial, verbosity):
    # Get list of annotation files
    gtname = "Music.xml"
    annFiles = getListOfRelativePathToFile( path2groundtruth, gtname )
    # Evaluate one file after the other and put results into evalList
    evalList = []
    for annFile in annFiles:
        # Get full path to groundtruth xml file
        path2xml_gt = os.path.join(path2groundtruth, annFile, gtname)
        # Get full path to expected submission xml file
        path2xml_sub = os.path.join(path2submission, annFile, subname)

        # Make sure it exists
        if os.path.exists(path2xml_sub) == False:
            if partial == False:
                print "%s > ERROR - missing submission file" % (os.path.join(annFile, gtname))
                e = eval.eval_zik(path2xml_gt, None, verbosity)
                evalList.append(e)                
        else:
            if verbosity > 1:
                print ""
                print "#### %s ERROR LIST ####" % (os.path.join(annFile, gtname))
            e = eval.eval_zik(path2xml_gt, path2xml_sub, verbosity)
            if verbosity > 0:
                print "%s > %s " % (os.path.join(annFile, gtname), e.description())
            evalList.append(e)

    return evalList


def full_eval_ads(path2groundtruth, path2submission, subname, partial, verbosity):
    # Get list of annotation files
    gtname = "Advertising.xml"
    annFiles = getListOfRelativePathToFile( path2groundtruth, gtname )
    # Evaluate one file after the other and put results into evalList
    evalList = []
    for annFile in annFiles:
        # Get full path to groundtruth xml file
        path2xml_gt = os.path.join(path2groundtruth, annFile, gtname)
        # Get full path to expected submission xml file
        path2xml_sub = os.path.join(path2submission, annFile, subname)

        # Make sure it exists
        if os.path.exists(path2xml_sub) == False:
            if partial == False:
                print "%s > ERROR - missing submission file" % (os.path.join(annFile, gtname))
                e = eval.eval_ads(path2xml_gt, None, verbosity)
                evalList.append(e) 
        else:
            if verbosity > 1:
                print ""
                print "#### %s ERROR LIST ####" % (os.path.join(annFile, gtname))
            e = eval.eval_ads(path2xml_gt, path2xml_sub, verbosity)
            if verbosity > 0:
                print "%s > %s " % (os.path.join(annFile, gtname), e.description())
            evalList.append(e) 

    return evalList

def usage():
    print "HELP full_eval.py :"
    print "  -g, --groundtruth  Path to annotation directory"
    print "  -s, --submission   Path to submission directory"
    print "  -n  --filename     Name of submission files. Default is submission.xml"
    print "  -m  --music        Only perform music evaluation"
    print "  -a  --ads          Only perform ads evaluation"
    print "  -p  --partial      Only evaluate available submission files"
    print "  -v  --verbosity    Set level of verbosity (default=0)"
    print "                     0 = only print global results"
    print "                     1 = same as 0 + print per-file results"
    print "                     2 = same as 1 + print list of errors"
    print "  -h, --help         Print this help"

if __name__ == '__main__':
    try:
    	opts, args = getopt.getopt(sys.argv[1:], "hampg:s:n:v:", ["help", "music", "ads", "partial", "groundtruth=", "submission=", "filename=", "verbosity="])
    except getopt.GetoptError, err:
    	# print help information and exit:
    	print str(err) # will print something like "option -a not recognized"
    	usage()
    	sys.exit(2)
    		
    path2groundtruth = "";
    path2submission = "";
    subName = "submission.xml";
    adsOnly = False
    zikOnly = False
    partial = False
    verbosity = 0
    # print opts
    # print args
    for opt, arg in opts:
    	if opt in ("-h", "--help"):
    		usage()
    		sys.exit()
    	elif opt in ("-a", "--ads"):
    	    adsOnly = True
    	elif opt in ("-m", "--music"):
    	    zikOnly = True
    	elif opt in ("-g", "--groundtruth"):
    		path2groundtruth = arg
    	elif opt in ("-s", "--submission"):
    		path2submission = arg
    	elif opt in ("-n", "--filename"):
    	    subName = arg
    	elif opt in ("-p", "--partial"):
    	    partial = True
    	elif opt in ("-v", "--verbosity"):
    	    verbosity = int(arg)
    	else:
    		assert False, "unhandled option"

    if len(path2submission) == 0:
    	print "Error : missing submission directory."
    	sys.exit(2)
    if len(path2groundtruth) == 0:
        print "Error : missing groundtruth directory."
        sys.exit(2)
    if adsOnly and zikOnly:
        print "Error : cannot use both --ads and --music options"    
        sys.exit(2)

    if adsOnly == False:
        results_zik = full_eval_zik(path2groundtruth, path2submission, subName, partial, verbosity)
        global_zik = eval.eval_result()
        for r in results_zik:
            global_zik.add(r)
        if verbosity > 0:
            print "----------------------------------------------"
        print "Music: ",
        global_zik.show()
        
    if zikOnly == False:
        results_ads = full_eval_ads(path2groundtruth, path2submission, subName, partial, verbosity)
        global_ads = eval.eval_result()
        for r in results_ads:
            global_ads.add(r)
        if verbosity > 0:
            print "----------------------------------------------"
        print "Ads:   ",
        global_ads.show()
    