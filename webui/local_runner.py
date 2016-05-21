import time
from app.jobs.statistic import usage_stats
while True:
    print "Run Usage"
    usage_stats()
    time.sleep(60)
