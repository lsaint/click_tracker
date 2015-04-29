
virtualenv  
virtualenvwrapper  

source /usr/local/bin/virtualenvwrapper.sh  
export WORKON_HOME=~/Envs  
mkvirtualenv tracker

  
pip install http://projects.unbit.it/downloads/uwsgi-lts.tar.gz  
pip install -r requirements.txt  
  

#nginx  
server {  
    listen 5000;  
    server_name xxxxxxxxxx;  
    location / {  
        include uwsgi_params;  
        uwsgi_pass unix:/tmp/click_tracker.sock;  
}  
  
./runserver.py  # test  
./start.sh      # depoly  
