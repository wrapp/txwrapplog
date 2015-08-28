import sys

from twisted.logger import ILogObserver, formatEvent, LogLevel, \
        jsonFileLogObserver, Logger, globalLogBeginner
from zope.interface import provider


Logger = Logger


noisey_keys = {'message', 'time', 'log_time', 'log_logger', 'log_format',
    'log_flattened', 'log_text', 'log_source', 'factory', 'log_io', 'isError'}

level_name = {
    LogLevel.debug: 'debug',
    LogLevel.info: 'info',
    LogLevel.warn: 'warning',
    LogLevel.error: 'error',
    LogLevel.critical: 'error',
}


def wrapp_observer(obs):
    @provider(ILogObserver)
    def wrapped(event):
        try:
            # If there is a failure, use the type and message to create the main msg.
            if 'failure' in event:
                f = event['failure']
                parts = [f.type.__name__, f.getErrorMessage()]
                msg = ' '.join(filter(None, parts))

            # Otherwise use normal event formatting to create the main msg.
            else:
                msg = formatEvent(event)

            new = {'msg': msg}

            # Process all keys of the event
            for k, v in event.items():

                # Filter out noise
                if k in noisey_keys:
                    continue

                # Normalize errors
                elif k == 'log_level':
                    k = 'level'
                    v = level_name[v]

                # Keep these but rename them
                elif k == 'log_namespace':
                    k = 'namespace'
                elif k == 'log_system':
                    k = 'system'

                new[k] = v

        except Exception as e:
            # Fallback to normal event processing
            new = event
            new['log_failure'] = str(e)

        obs(new)

    return wrapped


def start_logging(output=sys.stdout):
    json = jsonFileLogObserver(output, recordSeparator='')
    wrapp = wrapp_observer(json)
    globalLogBeginner.beginLoggingTo([wrapp])
