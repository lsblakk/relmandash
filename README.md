relmandash
==========

This project runs on Flask - follow the instructions below to check out the code!

#. Check out the code::

    git clone git://github.com/mozilla/relmandash.git
    
#. (optional) Create your virtualenv using virtualenvwrapper::

    mkvirtualenv --no-site-packages relmandash
    
#. If you need to, install pip::

    easy_install pip
    
#. Install the dependencies for relmandash::

    pip install -r requirements.txt

#. Create a config.py file and input your postgres database info::

		DB_URL='postgresql://user:password@localhost/database_name'
    
#. Run dashboard.py to try out the application locally::

    python runserver.py db_setup --> to set up database and run server
    python runserver.py         --> to run server only

# In a WSGI deploymnt scenario, make sure to add your virtualenv's site-packages to the WSGIPythonPath so that the app can find bztools and others