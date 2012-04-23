import web
import json

from src.parser import Parser
from tests.parser import ParserWrapper
from src.validation import validate as validate_expression

urls = (
    '/math\.py/validate', 'validate',
    '/math\.py/hint', 'hint',
    '/math\.py/step', 'Step',
    '/math\.py/answer', 'Answer',
)


def get_last_line():
    data = web.input(data='').data
    lines = map(str, data.split('\n'))

    # Get the last none empty line.
    for i in range(len(lines))[::-1]:
        last_line = lines[i].strip()

        if last_line:
            return last_line


class Step(object):
    def POST(self):
        web.header('Content-Type', 'application/json')

        try:
            last_line = get_last_line()

            if last_line:
                parser = ParserWrapper(Parser)
                response = parser.run([last_line])

                if response:
                    response = response.rewrite(include_step=True,
                            check_implicit=True)

                    if response:
                        return json.dumps({'step': str(response)})

            return json.dumps({'hint': 'No further reduction is possible.'})
        except Exception as e:
            return json.dumps({'error': str(e)})


class Answer(object):
    def POST(self):
        web.header('Content-Type', 'application/json')

        try:
            last_line = get_last_line()

            if last_line:
                parser = ParserWrapper(Parser)
                response = parser.run([last_line])

                if response:
                    steps = response.rewrite_all(include_step=True)

                    if steps:
                        hints, steps = zip(*steps)
                        return json.dumps({'hints': map(str, hints),
                                           'steps': map(str, steps)})

            return json.dumps({'hint': 'No further reduction is possible.'})
        except Exception as e:
            return json.dumps({'error': str(e)})


class hint(object):
    def POST(self):
        web.header('Content-Type', 'application/json')

        try:
            last_line = get_last_line()

            if last_line:
                parser = ParserWrapper(Parser)
                response = parser.run([last_line])
                response = parser.parser.give_hint()

                if response:
                    return json.dumps({'hint': str(response)})

            return json.dumps({'hint': 'No further reduction is possible.'})
        except Exception as e:
            return json.dumps({'error': str(e)})


class validate(object):
    def POST(self):
        web.header('Content-Type', 'application/json')

        data = web.input(data='').data
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

            return json.dumps({'validated': i - skipped})
        except Exception as e:
            i -= 1
            return json.dumps({'error': str(e), 'validated': i - skipped})


if __name__ == "__main__":
    app = web.application(urls, globals(), autoreload=True)
    app.run()
