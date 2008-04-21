"""Best goddamn .pythonrc file in the whole world.

This file is executed when the Python interactive shell is started if
$PYTHONSTARTUP is in your environment and points to this file. It's just
regular Python commands, so do what you will. Your ~/.inputrc file can greatly
complement this file."""

AUTHOR = 'Seth House'
CONTACT = 'seth@eseth.com'
LAST_MODIFIED = '$Date$'

##########################################################################

# Imports we need
import sys, os, readline, rlcompleter, atexit, pprint, __builtin__, __main__
from tempfile import mkstemp
from code import InteractiveConsole

# Imports we want
import datetime

# Color Support {{{1
###############

class TermColors(dict):
    """Gives easy access to ANSI color codes. Attempts to fall back to no color
    for certain TERM values. (Mostly stolen from IPython.)"""

    COLOR_TEMPLATES = (
        ("Black"       , "0;30"),
        ("Red"         , "0;31"),
        ("Green"       , "0;32"),
        ("Brown"       , "0;33"),
        ("Blue"        , "0;34"),
        ("Purple"      , "0;35"),
        ("Cyan"        , "0;36"),
        ("LightGray"   , "0;37"),
        ("DarkGray"    , "1;30"),
        ("LightRed"    , "1;31"),
        ("LightGreen"  , "1;32"),
        ("Yellow"      , "1;33"),
        ("LightBlue"   , "1;34"),
        ("LightPurple" , "1;35"),
        ("LightCyan"   , "1;36"),
        ("White"       , "1;37"),
        ("Normal"      , "0"),
    )

    NoColor = ''
    _base  = '\001\033[%sm\002'

    def __init__(self):
        if os.environ.get('TERM') in ('xterm-color', 'xterm-256color', 'linux',
                                    'screen', 'screen-256color', 'screen-bce'):
            self.update(dict([(k, self._base % v) for k,v in self.COLOR_TEMPLATES]))
        else:
            self.update(dict([(k, self.NoColor) for k,v in self.COLOR_TEMPLATES]))
_c = TermColors()

# Enable a History {{{1
##################

HISTFILE="%s/.pyhistory" % os.environ["HOME"]

# Read the existing history if there is one
if os.path.exists(HISTFILE):
    readline.read_history_file(HISTFILE)

# Set maximum number of items that will be written to the history file
readline.set_history_length(300)

def savehist():
    readline.write_history_file(HISTFILE)

atexit.register(savehist)

# Enable Color Prompts {{{1
######################

sys.ps1 = '%s>>> %s' % (_c['Green'], _c['Normal'])
sys.ps2 = '%s... %s' % (_c['Red'], _c['Normal'])

# Enable Pretty Printing for stdout {{{1
###################################

def my_displayhook(value):
    if value is not None:
        __builtin__._ = value
        pprint.pprint(value)
sys.displayhook = my_displayhook

# Welcome message {{{1
#################

WELCOME = """%(Green)s
The Python shell is coming at 'ya, punk!
%(Cyan)s
You've got color, history, and pretty printing.
(If your ~/.inputrc doesn't suck, you've also
got completion and vi-mode keybindings.)
%(LightPurple)s
Type \e to get an external editor.
%(Brown)s
Oh yeah, it is that cool.
%(Normal)s""" % _c

atexit.register(lambda: sys.stdout.write("""%(DarkGray)s
Sheesh, I thought he'd never leave. Who invited that guy?
%(Normal)s""" % _c))

# Django Helpers {{{1
################

def SECRET_KEY():
    "Generates a new SECRET_KEY that can be used in a project settings file." 

    from random import choice
    return ''.join(
            [choice('abcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*(-_=+)')
                for i in range(50)])

# If we're working with a Django project, set up the test environment
if os.environ.get('DJANGO_SETTINGS_MODULE', ''):
    from django.db.models.loading import get_models
    from django.test.client import Client
    from django.test.utils import setup_test_environment, teardown_test_environment

    class DjangoModels(object):
        def __init__(self):
            for m in get_models():
                setattr(self, m.__name__, m)

    A = DjangoModels()
    C = Client()
    setup_test_environment()

    print """%(LightBlue)s
Django environment detected.
* Your INSTALLED_APPS models have been imported into the namespace `A`.
* The Django test client is available as `C`.
* The Django test environment has been set up. To restore the normal
  environment call `teardown_test_environment()`.
%(Normal)s""" % _c
# Start an external editor with \e {{{1
##################################     
# http://aspn.activestate.com/ASPN/Cookbook/Python/Recipe/438813/

EDITOR = os.environ.get('EDITOR', 'vim')
EDIT_CMD = '\e'

class EditableBufferInteractiveConsole(InteractiveConsole):
    def __init__(self, *args):
        self.last_buffer = [] # This holds the last executed statement
        InteractiveConsole.__init__(self, *args)

    def runsource(self, source, *args):
        self.last_buffer = [ source ]
        return InteractiveConsole.runsource(self, source, *args)

    def raw_input(self, *args):
        line = InteractiveConsole.raw_input(self, *args)
        if line == EDIT_CMD:
            fd, tmpfl = mkstemp('.py')
            os.write(fd, '\n'.join(self.last_buffer))
            os.close(fd)
            os.system('%s %s' % (EDITOR, tmpfl))
            line = open(tmpfl).read()
            os.unlink(tmpfl)
            tmpfl = ''
            lines = line.split( '\n' )
            for i in range(len(lines) - 1): self.push( lines[i] )
            line = lines[-1]
        return line

c = EditableBufferInteractiveConsole()
# Update the InteractiveConsole's namespace with the current namespace
c.locals.update(__main__.__dict__)
c.interact(banner=WELCOME)

# Exit the Python shell on exiting the InteractiveConsole
sys.exit()
