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


import os
import sys
import getopt
import re

import metric
import yacastIO
import submissionIO

class Options:
    pass

def getListOfFingerprints( path2fingerprint ):
    f = open(path2fingerprint, 'r')
    fingerprint = {}
    for line in f:
        fingerprint[ line.rstrip()] = 1
    return fingerprint

def getListOfRelativePathToFile( mydir, filename ):
    fileList = []
    rootdir = os.path.normpath(mydir)
    for root, subFolders, files in os.walk(rootdir):
        for file in files:
            if file == filename:
                fileList.append(os.path.dirname(os.path.relpath(os.path.join(root,file), rootdir)))
    return fileList

def evaluateFile( groundTruthFile, submissionFile, options):
    
    # Evaluation result (dictonary, one entry per event type)
    result = {}
    
    # Annotations (dictonary, one entry per event type)
    groundtruth = yacastIO.YacastAnnotations(groundTruthFile)
    
    # Read start time and end time day restriction
    if options.limitedhours:
            # Faire la lecture des valeurs de debut et fin et les faire passer dans options
            # Read
            f = open(options.path2xml_ts, 'r')
            string_start=f.readline()
            string_end=f.readline()
            f.close()
            
            # Check format
            if (re.match(r'\d{2}:\d{2}:\d{2}',string_start)) and (re.match(r'\d{2}:\d{2}:\d{2}',string_end)):
                list_start=re.split(r':',string_start)
                list_end=re.split(r':',string_end)
            else:
                print "%s > ERROR - Start time (or End time) should be formated as HH:MM:SS" % (options.path2xml_ts)
                return None
        
            # Write data in options
            options.startH=int(list_start[0])
            options.startM=int(list_start[1])
            options.startS=int(list_start[2])
            options.endH=int(list_end[0])
            options.endM=int(list_end[1])
            options.endS=int(list_end[2])

    # Detections (dictionary, one entry per event type)
    submission  = submissionIO.Submission(submissionFile)
    
    # For each event type
    for eventType in groundtruth.eventList.keys():
        # Perform the evaluation
        if eventType in submission.detectionList.keys():
            result[eventType] = metric.compute_metric(groundtruth.eventList[eventType], submission.detectionList[eventType], options)
        else:
            result[eventType] = metric.compute_metric(groundtruth.eventList[eventType], [], options)
        
        # Store event type, participant ID and submission ID
        result[eventType].eventType = eventType
        result[eventType].participant = submission.participant
        result[eventType].submission = submission.ID
    
    return result

def evaluateDirectory(groundTruthDir, groundTruthFileName, submissionDir, submissionFileName, options):
    # List of path to directories containing the groundtruth files
    # (relative to groundTruthDir)
    groundTruthFiles = getListOfRelativePathToFile( groundTruthDir, groundTruthFileName)
    
    # Process all files and produce list of evaluation results
    results = {}
    for groundTruthFile in groundTruthFiles:
        # Full path to groundtruth XML file
        path2xml_gt = os.path.join(groundTruthDir, groundTruthFile, groundTruthFileName)
        if options.limitedhours:
            # Full path to groundtruth time slot file
            options.path2xml_ts = os.path.join(groundTruthDir, groundTruthFile, "TimeSlot.txt")
        # Full path to corresponding submission XML file
        path2xml_sub = os.path.join(submissionDir, groundTruthFile, submissionFileName)
        
        # Make sure it exists
        if os.path.exists(path2xml_sub) == False:
            if options.partial == False:
                print "%s > ERROR - missing submission file" % (path2xml_sub)
                return None
        else:
            if options.verbosity > 1:
                print "----------------------------------------------"
                print "ERROR LIST for %s" % (os.path.join(groundTruthFile, groundTruthFileName))
                print "----------------------------------------------"
            result = evaluateFile(path2xml_gt, path2xml_sub, options)
            if options.verbosity > 0:
                for eventType in result.keys():
                    print "%s | %s | %s" % (os.path.join(groundTruthFile, groundTruthFileName), eventType, result[eventType].description())
            for eventType in result.keys():
                if eventType not in results.keys():
                    results[eventType] = []
                results[eventType].append(result[eventType])
    
    return results

def usage():
    print "HELP full_eval.py :"
    print "  -g, --groundtruth  Path to groundtruth directory"
    print "  -G  --groundtruth-filename"
    print "                     Name of groundtruth files. Default is Music.xml"
    print "  -s, --submission   Path to submission directory"
    print "  -S  --submission-filename"
    print "                     Name of submission files. Default is submission.xml"
    print "  -p  --partial      Only evaluate available submission files"
    print "  -d  --skip2days    Skip events that starts the day before or ends the day after"
    print "  -f  --fingerprint  Path to list of available fingerprint"
    print "  -l  --limited-hours"
    print "                     Only evaluate on some chosen Time Slots. These time slots should be provided in TimeSlot.txt files, one for each GROUNDTRUTH file, located on the same directory than the corresponding MUSIC.xml GROUNDTRUTH file"
    print "  -v  --verbosity    Set level of verbosity (default=-1)"
    print "                    -1 = only print global results"
    print "                     0 = same as -1 + print command arguments"
    print "                     1 = same as 0 + print per-file results"
    print "                     2 = same as 1 + print list of errors"
    print "                     3 = same as 2 + print list of hits"
    print "  -h, --help         Print this help"
    print ""
    print "OUTPUT FORMAT"
    print "$ParticipantID$ $RunID$ | $EventType$ | Hit (Miss) / Total => $Hit$ ($Miss$) / $Total$ | FA1 (out) = $FA1$ ($FA1out$) | FA2 (out) = $FA2$ ($FA2out$) | R1 = $R1$ | R2 = $R2$ | R1.5 = $R1.5$"
    print "  $ParticipantID$: participant ID (from XML submission files)"
    print "  $RunID$: run ID (from XML submission files)"
    print "  $Hit$: number of hits (correct detection)"
    print "  $Total$: number of events to be detected"
    print "  $Miss$: number of misses"
    print "  $R1$: performance metric 2 ($Hit$ - $FA1$ - $FA1out$) / $Total$"
    print "  $R2$: performance metric 3 ($Hit$ - $FA2$ - $FA2out$) / $Total$"
    print "  $R1.5$: hybrid performance metric ($Hit$ - $FA2$ - $FA1out$) / $Total$"
    
    print "  $FA1$: number of false alarms (+1 for every incorrect detection)"
    print "         e.g.: If Detected = B C B and Groundtruth = A, then $FA1$ = 3"
    print "  $FA1out$: same as $FA1$ but dedicated to time intervals where no events should be detected"
    print "  $FA2$: same as $FA1$ but multiple errors for the same couple (groundtruth event/detected event) do not add up."
    print "         e.g.: If Detected = B C B and Groundtruth = A, then $FA2$ = 2 (one for B, and one for C)"
    print "  $FA2out$: same as $FA2$ but dedicated to time intervals where no events should be detected)"

if __name__ == '__main__':
    try:
        opts, args = getopt.getopt(sys.argv[1:], "hpg:G:s:S:v:df:l", ["help", "partial", "groundtruth=", "groundtruth-filename=", "submission=", "submission-filename=", "verbosity=", "skip2days", "fingerprint=","limited-hours"])
    except getopt.GetoptError, err:
        # print help information and exit:
        print str(err) # will print something like "option -a not recognized"
        usage()
        sys.exit(2)
    
    path2groundtruth = "";
    path2submission = "";
    gtName  = "Music.xml"
    subName = "submission.xml";
    options = Options()
    options.partial = False
    options.verbosity = -1
    options.skipTwoDaysEvents = False
    options.limitedhours = False
    path2fingerprint = "";
    for opt, arg in opts:
        if opt in ("-h", "--help"):
            usage()
            sys.exit()
        elif opt in ("-g", "--groundtruth"):
            path2groundtruth = arg
        elif opt in ("-G", "--groundtruth-filename"):
            gtName = arg
        elif opt in ("-s", "--submission"):
            path2submission = arg
        elif opt in ("-S", "--submission-filename"):
            subName = arg
        elif opt in ("-p", "--partial"):
            options.partial = True
        elif opt in ("-d", "--skip2days"):
            options.skipTwoDaysEvents = True
        elif opt in ("-f", "--fingerprint"):
            path2fingerprint = arg
        elif opt in ("-v", "--verbosity"):
            options.verbosity = int(arg)
        elif opt in ("-l", "--limited-hours"):
            options.limitedhours = True
        else:
            assert False, "unhandled option"
    
    if (options.verbosity > -1):
        print "$ " + ' '.join(sys.argv[0:])
    
    if len(path2submission) == 0:
        print "Error : missing submission directory."
        sys.exit(2)
    if len(path2groundtruth) == 0:
        print "Error : missing groundtruth directory."
        sys.exit(2)
    
    options.fingerprints = {}
    if len(path2fingerprint) != 0:
        # load list of available fingerprints as dictionary
        options.fingerprints = getListOfFingerprints( path2fingerprint )
    
    results = evaluateDirectory(path2groundtruth, gtName, path2submission, subName, options)
    
    metrics = {}
    for eventType in results.keys():
        metrics[eventType] = metric.Metric()
        metrics[eventType].participant = results[eventType][0].participant
        metrics[eventType].submission = results[eventType][0].submission
        for r in results[eventType]:
            metrics[eventType].add(r)
    
    for eventType in results.keys():
        if options.verbosity > 0:
            print "----------------------------------------------"
        print "%s %s | %s | %s" % (metrics[eventType].participant, metrics[eventType].submission, eventType, metrics[eventType].description())
