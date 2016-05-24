import time
from app.jobs.statistic import nginx_logs_stats
while True:
    print "Run Logs"
    nginx_logs_stats()
    print "Run Logs done, wait"
    time.sleep(60*10)

