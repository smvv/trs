# This file is part of TRS (http://math.kompiler.org)
#
# TRS is free software: you can redistribute it and/or modify it under the
# terms of the GNU Affero General Public License as published by the Free
# Software Foundation, either version 3 of the License, or (at your option) any
# later version.
#
# TRS is distributed in the hope that it will be useful, but WITHOUT ANY
# WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR
# A PARTICULAR PURPOSE.  See the GNU Affero General Public License for more
# details.
#
# You should have received a copy of the GNU Affero General Public License
# along with TRS.  If not, see <http://www.gnu.org/licenses/>.
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
