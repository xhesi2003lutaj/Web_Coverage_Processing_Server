from wdc.dbc import DatabaseConnection
from typing import Optional
from wdc import dbc
import requests
import xml.etree.ElementTree as ET
import urllib.parse

class Coverages:
    """
    Retrieval of a coverage from the server.
    """
    def fetch_coverage(self, query: Optional[str] = None) -> bytes:
        """
        Fetches the coverage from the server based on the constructed request URL.
        Args:
            query (str): Optional query to include in the request.
        Returns:
            bytes: The content of the fetched coverage.
        """
        # Include query in request URL if provided
        if query is not None:
            self.request_url += f"&query={query}"
        # Send GET request to the server and retrieve the response
        response = requests.get(self.request_url)
        # Check for any errors in the response
        response.raise_for_status()
        # Return the content of the response
        return response.content

    def _construct_request_url(self) -> str:
        """
        Constructs the request URL based on provided parameters.
        Returns:
            str: The constructed request URL.
        """
        request_url = f"{self.base_wcs_url}&request=GetCoverage&coverageId={self.coverage_id}&FORMAT={self.output_format}"
        if self.subset is not None:
            request_url += f"&SUBSET=ansi(\"{self.subset}\")"
        return request_url

    def __init__(self, connection: object, coverage_id: str, subset: Optional[str] = None, output_format: str = None):
        """
        Initializes a Coverages object to fetch a coverage with the given ID.
        """
        # Ensure the connection object is of the correct type
        assert isinstance(connection, DatabaseConnection)
        # Set attributes for connection details and coverage information
        self.connection = connection
        self.coverage_id = coverage_id
        self.subset = subset
        self.output_format = output_format
        # Check if output format is provided and supported by the server
        assert self.output_format in Capacities(self.connection).get_encodings()
        # Set base WCS URL and construct request URL
        self.base_wcs_url = connection.base_wcs_url
        self.request_url = self._construct_request_url()
 


class Coverage_id:
    
    def __init__(self, connection: object, coverage_id: str):
        """
        Initializing the object with connection details and coverage ID.
        """
        # Ensure the connection object is of the correct type
        assert isinstance(connection, dbc.DatabaseConnection)
        # Set the base WCS URL and request parameters
        self._base_wcs_url = connection.base_wcs_url
        self._request = '&request=DescribeCoverage'
        self._coverage_id = coverage_id

    def describe_coverage_xml(self, cis: Optional[str] = None) -> str:
        """
        .Fetching the description of the coverage from the server and returning it as XML.
        """
        # Check if the coverage ID and base WCS URL are set
        assert self._coverage_id is not None, "Coverage ID is required"
        assert self._base_wcs_url is not None, "Base WCS URL is required"

        # Handling the request to the server with or without without CIS versuon
        if cis is not None:
            response = requests.get(f"{self._base_wcs_url}{self._request}&coverageId={self._coverage_id}&outputType=GeneralGridCoverage")
        else:
            response = requests.get(f"{self._base_wcs_url}{self._request}&coverageId={self._coverage_id}")
        return response.text

    def describe(self, cis: Optional[str] = None) -> dict:
        """
        Parses the XML description of the coverage and returns a dictionary with the coverage information.
        """
        # Define namespaces for readability
        ns = {
            'gml': 'http://www.opengis.net/gml/3.2',
            'gmlrgrid': 'http://www.opengis.net/gml/3.3/rgrid'
        }
        # Parse the XML response from the server
        root = ET.fromstring(self.describe_coverage_xml(cis))

        # Extract envelope information
        envelope = root.find(".//gml:Envelope", namespaces=ns)
        axis_labels = envelope.get("axisLabels").split()
        uom_labels = envelope.get("uomLabels").split()

        # Extract the lower and upper corners of the envelope
        lower_corner = [x for x in envelope.find("./gml:lowerCorner", namespaces=ns).text.split()]
        upper_corner = [x for x in envelope.find("./gml:upperCorner", namespaces=ns).text.split()]

        limits = root.find(".//gml:limits", namespaces=ns)
        low_values = None
        high_values = None

        # Handle different XML formats
        #Credentials, Generated by AI
        if limits is not None:
            grid_envelope = limits.find("./gml:GridEnvelope", namespaces=ns)
            if grid_envelope is not None:
                # Extract the low and high values of the coverage
                low_element = grid_envelope.find("./gml:low", namespaces=ns)
                high_element = grid_envelope.find("./gml:high", namespaces=ns)
                if low_element is not None:
                    # Split the values and convert them to floats
                    low_values = [float(x) for x in low_element.text.split()]
                if high_element is not None:
                    high_values = [float(x) for x in high_element.text.split()]
            # If the limits element is not present, we try to find the domainSet element instead
        else:
            domain_set = root.find(".//gml:domainSet", namespaces=ns)
            if domain_set is not None:
                grid = domain_set.find(".//gmlrgrid:ReferenceableGridByVectors", namespaces=ns)
                if grid is not None:
                    grid_envelope = grid.find("./gml:limits/gml:GridEnvelope", namespaces=ns)
                    if grid_envelope is not None:
                        # Same as before, but inside of another element
                        low_element = grid_envelope.find("./gml:low", namespaces=ns)
                        high_element = grid_envelope.find("./gml:high", namespaces=ns)
                        if low_element is not None:
                            low_values = [float(x) for x in low_element.text.split()]
                        if high_element is not None:
                            high_values = [float(x) for x in high_element.text.split()]

        # Create dictionary with coverage information
        info_dict = {}
        for i, (axis_label, uom_label) in enumerate(zip(axis_labels, uom_labels)):
            geo_extent = [lower_corner[i], upper_corner[i]]
            grid_extent = [low_values[i] if low_values is not None else None, high_values[i] if high_values is not None else None]
            info_dict[axis_label] = {"UoM": uom_label, "Geo Extent": geo_extent, "Grid Extent": grid_extent}

        return info_dict


class ProcessCoverage:
    """
    Processing a coverage on the server.
    """
    # Upon initialization, we receive the connection object and the query to be processed.
    def __init__(self, connection: object, query: str) -> None:
        # Ensure that the connection object is of the correct type
        assert isinstance(connection, DatabaseConnection)
         # Set the base WCS URL and the query
        self.base_wcs_url = connection.base_wcs_url
        self.query = query
        # Construct the request URL
        self.request_url = self._construct_request_url()

    def _construct_request_url(self) -> str:
        """Constructs the request URL for processing the coverage."""
        # Create the request URL with the appropriate parameters
        request_url = f"{self.base_wcs_url}&request=ProcessCoverage"
        return request_url

    def fetch_coverage(self) -> bytes:
        """Fetches the processed coverage from the server."""
        # Append the query to the request URL
        self.request_url += f"&query={self.query_to_url()}"
         # Send a GET request to the server and retrieve the response
        response = requests.get(self.request_url)
        # Check for any errors in the response
        response.raise_for_status()
        # Return the content of the response
        return response.content

    def query_to_url(self) -> str:
        return urllib.parse.quote(self.query)

class Capacities:
    """
      Handles Capacities requests.
    """

    def __init__(self, connection: object):
        """
        Initialize Capacities object with connection details.
        Args:
          connection (database_connection.DatabaseConnection): The connection object to the database.
        """
        # Ensure the connection object is of the correct type
        assert isinstance(connection, dbc.DatabaseConnection)
        # Set the base WCS URL and request parameters
        self._base_wcs_url = connection.base_wcs_url
        self._request = '&request=GetCapabilities'
    def get_coverage_ids(self) -> list[str]:

        root = ET.fromstring(self.get_capacities())
        coverage_ids = [coverage_summary.find('wcs20:CoverageId', namespaces={'wcs20': 'http://www.opengis.net/wcs/2.0'}).text
            for coverage_summary in root.findall('wcs20:Contents/wcs20:CoverageSummary', namespaces={'wcs20': 'http://www.opengis.net/wcs/2.0'})]
        return coverage_ids

    def get_capacities(self) -> str:
        """
        Returns the response from the server.
        """
        # Send a GetCapabilities request and retrieve the response
        response = requests.get(f"{self._base_wcs_url}{self._request}")
        response.raise_for_status()
        return response.text

    
    def get_encodings(self) -> list[str]:
        """
        List of encodings
        """
        root = ET.fromstring(self.get_capacities())

        encodings = root.findall('.//wcs20:formatSupported', namespaces={'wcs20': 'http://www.opengis.net/wcs/2.0'})

        supported_encodings = [encoding_elem.text for encoding_elem in encodings]
        return supported_encodings
