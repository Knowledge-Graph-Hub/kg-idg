from unittest import TestCase, mock
import os
import shutil

import mysql.connector.errors
import psycopg2

from kg_idg.utils.sql_utils import make_temp_mysql_db, make_temp_postgres_db, \
                                    process_mysql_dump, process_postgresql_dump, \
                                    process_data_dump

class TestSQLUtils(TestCase):

    def setUp(self) -> None:
        self.input_dir = 'tests/resources/snippets/'
        self.output_dir = 'tests/resources/'

    # DB operations will fail unless a corresponding
    # server is running, so we test that

    def test_make_temp_mysql_db_fails(self):
        with self.assertRaises(mysql.connector.errors.DatabaseError):
            connection = make_temp_mysql_db("fake","test")

    def test_make_temp_postgres_db_fails(self):
        with self.assertRaises(psycopg2.OperationalError):
            connection = make_temp_postgres_db("fake","test")
    
    @mock.patch('kg_idg.utils.sql_utils.make_temp_mysql_db')
    def test_process_data_dump_mysql(self, mock_make_temp_mysql_db):
        success = process_data_dump("test", 
                            "mysql", 
                            "test_mysql.sql", 
                            ["data_type"], 
                            self.input_dir, 
                            self.output_dir, 
                            list_tables=True)
        self.assertTrue(success)
    
    @mock.patch('kg_idg.utils.sql_utils.make_temp_postgres_db')
    @mock.patch('os.system')
    @mock.patch('psycopg2.connect')
    def test_process_data_dump_postgresql(self, mock_make_temp_postgres_db, 
                                            mock_system, mock_connect):
        success = process_data_dump("test", 
                            "postgres", 
                            "test_postgres.sql", 
                            ["data_type"], 
                            self.input_dir, 
                            self.output_dir, 
                            list_tables=False)
        self.assertTrue(success)
    
    def test_process_data_dump_other(self):
        success = process_data_dump("test", 
                            "dbdbdb", 
                            "test_mysql.sql", 
                            ["data_type"], 
                            self.input_dir, 
                            self.output_dir, 
                            list_tables=True)
        self.assertFalse(success)