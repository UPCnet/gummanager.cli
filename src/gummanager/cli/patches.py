import docopt
import prettytable
import re
import sys


def put_spacing(string):
    lines = string.split('\n')
    newlines = []
    lastline = ''

    for line in lines:
        match_current_line = re.match(r'\s+gum\s+([^\s]+)', line)
        if match_current_line:
            match_last_line = re.match(r'\s+gum\s+([^\s]+)', lastline)
            if match_last_line:
                if match_current_line.groups()[0] != match_last_line.groups()[0]:
                    line = '\n' + line

        newlines.append(line)
        lastline = line
    return '\n'.join(newlines)


#monkey patch docopt, to add spaces between targets
def extras(help, version, options, doc):

    if help and any((o.name in ('-h', '--help')) and o.value for o in options):

        print(put_spacing(doc))

        sys.exit()
    if version and any(o.name == '--version' and o.value for o in options):
        print(version)
        sys.exit()

#monkeypatch prettytable to avoid counting blessings color codes
prettytable._re = re.compile("\x1b[\[\(][0-9B]*m?")


class DocoptExit(SystemExit):

    """Exit in case user invoked program with incorrect arguments."""

    usage = ''

    def __init__(self, message=''):
        SystemExit.__init__(self, (message + '\n' + put_spacing(self.usage) + '\n'))

docopt.extras = extras
docopt.DocoptExit = DocoptExit
