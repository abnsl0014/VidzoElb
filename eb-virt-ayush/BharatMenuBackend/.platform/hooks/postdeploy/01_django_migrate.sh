#!/bin/bash

source "$PYTHONPATH/activate" && {
    
    if [[ $EB_IS_COMMAND_LEADER == "true" ]];
    then 
        # log which migrations have already been applied

        python3 manage.py showmigrations;

        python3 manage.py makemigrations --noinput;
        
        # migrate
        python3 manage.py migrate --noinput;

        python3 manage.py createsu

        python3 manage.py collectstatic --noinput;

        export CPPFLAGS=-I/usr/local/opt/openssl/include 
        export LDFLAGS=-L/usr/local/opt/openssl/lib 
        pip install pycurl --global-option='--with-openssl'
    else 
        echo "this instance is NOT the leader";
    fi
    
}