from  apiv2.classes.connections import CSAPI_Connections
_conn     = CSAPI_Connections()
_redisconn= _conn._redis_conn()
_pretty   = False
from apiv2.classes.consoleapi import ConsoleAPI
from django.core.signals import request_started
from django.dispatch import receiver

@receiver(request_started)
def request_started_callback(sender, **kwargs):
    ConsoleAPI.time_start()
    print(sender)

    pass