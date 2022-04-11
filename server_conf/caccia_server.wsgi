import sys
from os.path import realpath, dirname
sys.path.insert(0, dirname(realpath(__file__)))

from pari_server import create_app
application = create_app()