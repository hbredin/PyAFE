import time
import datetime

class DateTimeRange (object):
	"""docstring for DateTimeRange"""
	def __init__(self, dtStart, dtStop):
		super(DateTimeRange, self).__init__()
		self.dtStart = dtStart
		self.dtStop  = dtStop
	
	def containsDateTime(self, dt):
		#       self starts before dt       and  self stops after dt
		return ((cmp(dt, self.dtStart) >= 0) and (cmp(self.dtStop, dt) >= 0)) 
	
	def containsDateTimeRange(self, dtr):
		#       self starts before dtr               and self stops after dtr
		return ((cmp(dtr.dtStart, self.dtStart) >= 0) and (cmp(self.dtStop, dtr.dtStop) >= 0))
	
	def compareStart(self, dtr):
		return cmp(self.dtStart, dtr.dtStart)
