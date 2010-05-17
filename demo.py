import eval

path2xml_ad  = "xml_files/Advertising.xml"
path2xml_zik = "xml_files/Music.xml"
path2xml_sub = "xml_files/submission.xml"

ad = eval.eval_ads(path2xml_ad, path2xml_sub)
zik = eval.eval_zik(path2xml_zik, path2xml_sub)

print "Eval Advertisement:"
ad.show()
print ""
print "Eval Music:"
zik.show()
