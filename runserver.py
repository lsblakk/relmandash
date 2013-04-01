import sys
from relmandash import app, init_db

if __name__ == "__main__":
    if len(sys.argv) > 1:
        if sys.argv[1] == 'db_setup':
            init_db()
            
    app.run(debug=True)
