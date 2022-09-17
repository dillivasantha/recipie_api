#because of structure core->management->commands , Django identifies this wait_for_db
"""there will be situations where 1. app starts
     2. db service starts but postgres db is not ready for execution 
     (example laptop starts but it takes time for chrome to start)
     so we need to make app/project wait till the db is up completely 
     so we wait for db ready or else we might get OperationalError (in case of psycopg2)

"""
"""
    Django command to wait for the database to be avaiable 

"""
from django.core.management.base import BaseCommand # which has check method to check database
import time
from psycopg2 import OperationalError as Psycopg2OpError
from django.db.utils import OperationalError # django throws when db is not ready and app tries to connect 


class Command(BaseCommand):
    """Django command to wait for databse"""
    # when call_command is called , this method is the one which executes
    def handle(self,*args, **kwargs):
        """ method call command 
        """
        self.stdout.write("Waiting for Database to be ready ")
        db_up = False
        while not db_up:
            try:
                self.check(databases=['default'])
                db_up = True
            except (Psycopg2OpError, OperationalError):
                self.stdout.write("Database unavaiable and waiting 1 second")
                time.sleep(1)
        self.stdout.write("Data base avaiable !!")