
virtualenv  
virtualenvwrapper  
  
source /usr/local/bin/virtualenvwrapper.sh  
  
pip install http://projects.unbit.it/downloads/uwsgi-lts.tar.gz  
pip install -r requirements.txt  
  
  
./runserver.py  # test  
./start.sh      # depoly  
