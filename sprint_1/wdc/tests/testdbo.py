import unittest
from unittest.mock import Mock
import sys
sys.path.append("..")
from dco import Datacube

# Class to test Datacube class and it's methods
class TestDatacube(unittest.TestCase):
    def setUp(self):
        # Mock DatabaseConnection object
        self.mock_connection = Mock()

    def test_slice_and_execute_image(self):
        # Mock describe and fetch_coverage methods
        self.mock_connection.describe.return_value = {"axes": ["ansi", "Lat", "Lon"], "shape": [365, 180, 360]}
        self.mock_connection.fetch_coverage.return_value = b'PNG_IMAGE_DATA'

        # Create Datacube 
        datacube = Datacube(self.mock_connection, coverage_id='AvgTemperatureColorScaled', encode='image/png')

        # Slice datacube
        modify_ans = {"ansi": "2000-04"}
        slice_datacube = datacube.slice(modify_ans)

        # Mock fetch_coverage method after slice operation
        slice_datacube.execute()

        # Assert calls
        self.mock_connection.describe.assert_called_once_with('AvgTemperatureColorScaled')
        self.mock_connection.fetch_coverage.assert_called_once()

        # Assert the result
        expected_result = b'PNG_IMAGE_DATA' 
        self.assertEqual(result, expected_result)

    def test_slice_and_execute_csv(self):
        # Mock describe and fetch_coverage methods
        self.mock_connection.describe.return_value = {"axes": ["ansi", "Lat", "Lon"], "shape": [365, 180, 360]}
        self.mock_connection.fetch_coverage.return_value = b'CSV_DATA'

        # Create and slice Datacube
        datacube = Datacube(self.mock_connection, coverage_id='AvgLandTemp', encode='text/csv')
        subset = {"ansi": ("2014-01", "2014-12"), "Lat": (53.08), "Lon": (8.80)}
        slice_datacube = datacube.slice(subset)

        # Mock fetch_coverage method after slicing
        slice_datacube.execute()

        # Assert calls
        self.mock_connection.describe.assert_called_once_with('AvgLandTemp')
        self.mock_connection.fetch_coverage.assert_called_once()

        # Assert the result
        expected_result = b'CSV_DATA' 
        self.assertEqual(result, expected_result)

    def test_get_image(self):
        # Mock fetch_coverage method
        self.mock_connection.fetch_coverage.return_value = b'PNG_IMAGE_DATA'

        # Create Datacube 
        datacube = Datacube(self.mock_connection, coverage_id='AvgTemperatureColorScaled', encode='image/png')

        # Fetch datacube
        datacube.get('2014-07')

        # Assert call
        self.mock_connection.fetch_coverage.assert_called_once()

    def test_modify_and_execute_image(self):
        # Mock describe and fetch_coverage methods
        self.mock_connection.describe.return_value = {"axes": ["ansi", "Lat", "Lon"], "shape": [365, 180, 360]}
        self.mock_connection.fetch_coverage.return_value = b'MODIFIED_PNG_IMAGE_DATA'

        # Create and modify Datacube 
        datacube = Datacube(self.mock_connection, coverage_id='AvgTemperatureColorScaled', encode='image/png')
        modify_ans1 = {"ansi": "2000-02-01"}
        subset_dc = datacube.slice(modify_ans1)

        # Mock fetch_coverage method after modification
        subset_dc.execute()

        # Assert calls
        self.mock_connection.describe.assert_called_once_with('AvgTemperatureColorScaled')
        self.mock_connection.fetch_coverage.assert_called_once()

        # Assert the result
        expected_result = b'PNG_IMAGE_DATA'   
        self.assertEqual(result, expected_result)

if __name__ == '__main__':
    unittest.main()
