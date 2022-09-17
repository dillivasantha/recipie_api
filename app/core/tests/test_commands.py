"""
Test custom Django management commands.
"""
from django.test import SimpleTestCase
from unittest.mock import patch
from psycopg2 import OperationalError as Psycopg2OpError
from django.core.management import call_command
from django.db.utils import OperationalError


@patch('core.management.commands.wait_for_db.Command.check')
class CommandTests(SimpleTestCase):
    """Test commands
    """
    def test_wait_for_db_ready(self,patched_check):
        """test to check if db is ready 
            mock the db ready response by calling function in wait_for_db.py 
            but here we can mock that return_value to true
            core.management.commands.wait_for_db.Command.check, 
            where check is a method inside which gets called to check db ready
        """

        # returns true confirming db is ready 
        patched_check.return_value = True

        # calls the function in wait_for_db.py 
        call_command('wait_for_db')
        
        # as db ready by single call no need to retry so called once 
        patched_check.assert_called_once_with(databases = ['default'])

    @patch('time.sleep')   
    def test_wait_for_db_delay(self,patched_sleep,patched_check):
        """ tests to check if any error or exception arised , 
                when db is not ready and delayed 
                we use side_effect of patched object when we have any exception to return 
        """

        # returns error each time with different error , total 6 times triying
        patched_check.side_effect = [Psycopg2OpError]*2+[OperationalError]*3+[True]
        
        # calls the function in wait_for_db.py 
        call_command('wait_for_db')

        self.assertEqual(patched_check.call_count, 6)

        patched_check.assert_called_with(databases = ['default'])
        