import sys, os
from srvadm import db
from srvadm import app

if __name__ == '__main__':
    if len(sys.argv) == 2:
        if sys.argv[1] == 'init':
            db.create_all()
        elif sys.argv[1] == 'run':
            app.run(host='0.0.0.0', port=5000)
