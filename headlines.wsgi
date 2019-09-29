activate_this = '/var/www/headlines/hlvenv/bin/activate_this.py'
exec(open(activate_this).read(),dict(__file__=activate_this))

import sys
sys.path.insert(0, "/var/www/headlines")
from headlines import app as application

