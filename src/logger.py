import logging
import logging.config
import sys

try:
    import config as cfg
except ImportError:
    cfg = object()

import default_config as default

try:
    logging.basicConfig(level=logging.DEBUG,
                        format=getattr(cfg, 'LOG_FORMAT', default.LOG_FORMAT),
                        filename=getattr(cfg, 'LOG_FILE', default.LOG_FILE),
                        filemode='a')
except IOError as e:  # pragma: no cover
    print >>sys.stderr, 'warning: IOError raised: "%s"' % str(e)


def logger(name):
    return logging.getLogger(name)


def filter_non_ascii(data):
        return ''.join(map(lambda x: 33 < ord(x) < 125 and x or '.', data))
