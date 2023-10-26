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
    else 
        echo "this instance is NOT the leader";
    fi
    
}