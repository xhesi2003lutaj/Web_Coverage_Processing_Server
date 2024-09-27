import unittest
import sys
sys.path.append("..")
from dbc import DatabaseConnection

# Very simple test class for the Database Connection object
class TestDatabaseConnection(unittest.TestCase):
    def test_initialization(self):
        # Set up a real DatabaseConnection instance
        db_url = "https://ows.rasdaman.org/rasdaman/ows"
        db_connection = DatabaseConnection(database_url=db_url)

        # Check if DatabaseConnection is properly initialized
        self.assertEqual(db_connection.WCPS_EndPoint, db_url)
        self.assertEqual(db_connection.base_wcs_url, db_url + "?service=WCS&version=2.1.0")

if __name__ == '__main__':
    unittest.main()
