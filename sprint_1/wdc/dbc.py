class DatabaseConnection:
    """A class representing a database connection to the WCPS server"""

    def __init__(self,database_url):
        self.WCPS_EndPoint =database_url 
        

        self.base_wcs_url = self.WCPS_EndPoint + "?service=WCS&version=2.1.0"
