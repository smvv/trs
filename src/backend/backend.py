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
from tornado.web import RequestHandler, Application

from src.parser import Parser
from tests.parser import ParserWrapper
from src.validation import validate as validate_expression
import sys
import traceback


# Log debug information
from logging import getLogger, DEBUG
getLogger().setLevel(DEBUG)


DEFAULT_PORT = 8888
ROUTER_DEBUG_MODE = True


def get_last_line(handler):
    data = handler.get_argument('data')
    lines = map(str, data.split('\n'))

    # Get the last none empty line.
    for i in range(len(lines))[::-1]:
        last_line = lines[i].strip()

        if last_line:
            return last_line


def format_exception(e):
    tb = sys.exc_info()[2]
    return {'error': str(e), 'traceback': traceback.format_tb(tb)}


class Step(RequestHandler):
    def post(self):
        try:
            last_line = get_last_line(self)

            if last_line:
                parser = ParserWrapper(Parser)
                response = parser.run([last_line])

                if response:
                    response = parser.rewrite(include_step=True,
                            check_implicit=True)

                    if response:
                        hint, step = response
                        self.write({'step': str(step), 'hint': str(hint)})
                        return

            self.write({'hint': 'No further reduction is possible.'})
        except Exception as e:
            self.write(format_exception(e))


class Answer(RequestHandler):
    def post(self):
        try:
            last_line = get_last_line(self)

            if last_line:
                parser = ParserWrapper(Parser)
                response = parser.run([last_line])

                if response:
                    steps = parser.rewrite_all(include_steps=True)

                    if steps:
                        out = []

                        for h, s in steps:
                            out.append(dict(hint=str(h), step=str(s)))

                        self.write({'steps': out})
                        return

            self.write({'hint': 'No further reduction is possible.'})
        except Exception as e:
            self.write(format_exception(e))


class Hint(RequestHandler):
    def post(self):
        try:
            last_line = get_last_line(self)

            if last_line:
                parser = ParserWrapper(Parser)
                response = parser.run([last_line])
                response = parser.parser.give_hint()

                if response:
                    self.write({'hint': str(response)})
                    return

            self.write({'hint': 'No further reduction is possible.'})
        except Exception as e:
            self.write(format_exception(e))


class Validate(RequestHandler):
    def post(self):
        data = self.get_argument('data')
        lines = map(str, data.split('\n'))

        i = 0
        skipped = 0

        try:
            # Get the first none empty line.
            for i in range(0, len(lines)):
                last_line = lines[i].strip()

                if not last_line:  # or last_line in ['?']:
                    skipped += 1
                    continue

                break

            # Validate each none empty line with the following none empty line.
            for i in range(i + 1, len(lines)):
                line = lines[i].strip()

                if not line:  # or line in ['?']:
                    skipped += 1
                    continue

                if not validate_expression(last_line, line):
                    i -= 1
                    break

                last_line = line

            self.write({'validated': i - skipped})
        except Exception as e:
            i -= 1
            self.write(format_exception(e) + {'validated': i - skipped})


urls = [
    ('/math\.py/validate', Validate),
    ('/math\.py/hint', Hint),
    ('/math\.py/step', Step),
    ('/math\.py/answer', Answer),
]

app = Application(urls, debug=ROUTER_DEBUG_MODE)


def start_server(app, port):
    from tornado.ioloop import IOLoop
    from tornado.options import enable_pretty_logging

    enable_pretty_logging()

    app.listen(port)
    IOLoop.instance().start()


if __name__ == '__main__':
    start_server(app, int(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_PORT)
