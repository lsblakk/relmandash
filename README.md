relmandash
==========

This project runs on Flask - follow the instructions below to check out the code!

#. Check out the code::

    git clone git://github.com/mozilla/relmandash.git
    
#. (optional) Create your virtualenv using virtualenvwrapper::

    mkvirtualenv --no-site-packages relmandash
    
#. Install pip::

    easy_install pip
    
#. Install the dependencies for relmandash::

    pip install -r requirements.txt
    
#. Run dashboard.py to try out the application locally::

    python dashboard.py db_setup --> to set up database and run server
    python dashboard.py         --> to run server only

# In a WSGI deploymnt scenario, make sure to add your virtualenv's site-packages to the WSGIPythonPath so that the app can find bztools and others