import time
from app.jobs.statistic import process_logs_stats
while True:
    print "Run Logs"
    process_logs_stats()
    print "Run Logs done, wait"
    time.sleep(75)

