import requests
import sched
import time

class StatusReporter:
    def __init__(self, endpoint, handle):
        """
        endpoint: Url where to check in. Example: http://localhost:123/.
        handle:   Handle of this service in the status monitor. Must match the status-monitor config entry exactly.
        """
        self.endpoint = endpoint
        if not self.endpoint.endswith('/'):
            self.endpoint += '/'
        
        self.handle = handle
        
        self.scheduler = sched.scheduler(time.time, time.sleep)
        
    def start(self):
        self.scheduler.enter(0, 1, self.__report)
        self.scheduler.run()
        
    def __report(self):
        interval = 60
        try:
            response = requests.get(f'{self.endpoint}{self.handle}/checkin')
            
            if response.status_code != 200:
                raise ReporterException(f"Endpoint sent status {response.status_code}")
            json = response.json()
            if not json['ok']:
                raise ReporterException(f"Endpoint was not ok: {json}")
            
            # Check in 10 seconds before the limit elapses
            interval = min(0, json['next_checkin'] * 60 - 10)
        except Exception as e:
            raise ReporterException(e)
        finally:
            self.scheduler.enter(interval, 1, self.__report)
    
class ReporterException(Exception):
    pass
