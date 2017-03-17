import os
import sys
from datetime import datetime
from collections import OrderedDict
from twisted.logger import ILogObserver, formatEvent, LogLevel, \
        jsonFileLogObserver, Logger, globalLogBeginner
from zope.interface import provider


# Re-exported for convenience
Logger = Logger


noisey_keys = {'message', 'time', 'log_time', 'log_logger', 'log_format',
    'log_flattened', 'log_text', 'log_source', 'factory', 'log_io', 'isError'}

level_name = {
    LogLevel.debug: 'debug',
    LogLevel.info: 'info',
    LogLevel.warn: 'warning',
    LogLevel.error: 'error',
    LogLevel.critical: 'error', # wep-007 does not support critical
}


def wrapp_observer(output, service=None):
    json = jsonFileLogObserver(output, recordSeparator='')
    service = service or os.environ.get('SERVICE_NAME')

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

            new = OrderedDict([
                ('level', level_name[event.pop('log_level')]),
                ('msg', msg),
                ('service', service),
                ('timestamp', _timestamp())

            ])

            if 'log_namespace' in event:
                new['namespace'] = event.pop('log_namespace')

            if 'log_system' in event:
                new['system'] = event.pop('log_system')

            # Keep all keys except the noise.
            for k, v in sorted(event.items()):
                if k not in noisey_keys:
                    new[k] = v

        except Exception as e:
            # Fallback to normal event processing
            new = event
            new['log_failure'] = str(e)

        output.write(new['level'].upper() + ' ')
        json(new)

    return wrapped


def _timestamp():
    return datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")


def start_logging(output=sys.stdout):
    wrapp = wrapp_observer(output)
    globalLogBeginner.beginLoggingTo([wrapp])
