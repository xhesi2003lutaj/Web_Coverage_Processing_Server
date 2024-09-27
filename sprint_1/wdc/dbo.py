from wdc.dbc import DatabaseConnection
from wdc.validation_wrapper.coverages import ProcessCoverage, Coverage_id, Coverages, Capacities
from wdc.src.action import Action 
from typing import List, Tuple

class Axis:
    def __init__(self, name):
        self.name = name

    def __call__(self, selection):
        if isinstance(selection, (int, float)):
            return f"{self.name}({selection})"
        elif isinstance(selection, str) or (isinstance(selection, tuple) and all(isinstance(s, str) for s in selection)):
            if isinstance(selection, tuple):
                lo, hi = selection
                selection = f'"{lo}":"{hi}"'
            elif isinstance(selection, str):
                selection = f'"{selection}"'
            return f'{self.name}({selection})'
        elif isinstance(selection, tuple):
            lo, hi = selection
            return f"{self.name}({lo}:{hi})"
        else:
            raise ValueError(f"Invalid selection type for axis {self.name}: {type(selection)}")
class Datacube:
    """
    Datacube object to ineract with rasdaman, retrieve, manipulate datacubes.
        """

    def __init__(self, connection: object, coverage_id: str, encode: str = None):
        """
        Initializing the datacube object, details:
                --connection
                --coverage_id
                --optional parameter for encoding
        Ensuring that the provided connection object is an instance of DatabaseConnection.
        Retrieving information about the datacube using the data() method.
        Initializing an empty list operations to store operations to be applied to the datacube.
        Setting the initial value of covExpr attribute to "$c", which represents the coverage expression.
                """
        assert isinstance(connection, DatabaseConnection)
        self.connection = connection
        self.coverage_id = coverage_id
        self._info = self.data()
        self.operations = []
        self.encode = encode
        self.covExpr = "$c"
        if self.encode and self.encode not in Capacities(self.connection).get_encodings():
            raise ValueError(f"Invalid encoding: {encode}")

    def _generate_wcps_query(self) -> str:
        """
        Given supported operations, generating queries ($c represents the coverage epression)
        """
        query = f"for $c in ({self.coverage_id}) return "
        # For each operation in the list, apply the operation to the query
        for op in self.operations:
            return_query = f"{self._apply_operation(op)}"
        # Once all operations have been put together, we encode the query with the specified encoding
        return_query = self.encode_format(return_query)
        # Finally, add it to the first part of the query
        query += return_query
        return query

    def execute(self):
        """
        Calling the generate funtion and executing the query
        """
        if not self.operations:
            raise ValueError("No operations specified")
        # Code to generate the WCPS query based on the operations
        query = self._generate_wcps_query()

        # Execute the query and return the result
        get_request = ProcessCoverage(self.connection, query=query)
        # Reset the covExpr attribute so that we can run execute multiple times
        self.covExpr = "$c"
        return get_request.fetch_coverage()
        #return query

    def data(self, cis: str = None) -> dict:
        """
        Retrieves the description of the datacube from the server.
        Args:
            cis (str): CIS version.
        Returns:
            dict: The description of the datacube.
        """
        describe_request = Coverage_id(self.connection, self.coverage_id)
        return describe_request.describe(cis)

    def get(self, subset: str = None) -> bytes:
        """
        Fetches the datacube from the server.
        Args:
            subset (str): The subset of the datacube to fetch.
            output_format (str): The format of the output data.
        Returns:
            bytes: The datacube in the specified format.
        """
        get_request = Coverages(self.connection, self.coverage_id, subset, self.encode)
        return get_request.fetch_coverage()

    def slice(self, slices: dict = None) -> str:
        """
        Slice the datacube based on the given data.
        Args:
            slices (dict): A dictionary containing the slices for each axis.
        """
        # We create a new operation object and append it to the list of operations
        op = Action('subset', [self], slices=slices)
        self.operations.append(op)
        return self


    def _apply_operation(self, op: Action) -> str:
        """
        Apply the given operation to the WCPS query.
        """
        op_type = op.op_type
        if op_type == 'subset':
            slices = op.kwargs['slices']
            query = self._apply_slice(slices)
        elif op_type == 'scale':
            scale_factor = op.kwargs.get('scale_factor')
            scale_expr = self._apply_scale(scales=scale_factor)
            query = f"{scale_expr}"
        # More operations to be added in future sprints
        return query

    # Helper functions to apply subset and scale operations
    def _apply_slice(self, slices: dict = None) -> str:
        axis_labels = self._info.keys()

        subset_expr = []
        for axis, selection in slices.items():
            if axis not in axis_labels:
                raise ValueError(f"Invalid axis name: {axis}, possible axes are: {axis_labels}")

            axis_instance = Axis(axis)
            subset_expr.append(axis_instance(selection))

    # Finally, we create the subset query and update the covExpr attribute
        subset_query = f"{self.covExpr}[{', '.join(subset_expr)}]"
        self.covExpr = subset_query

        return subset_query

    def encode_format(self, query: str) -> str:
        """
        Encode the given query with the specified encoding.
        Args:
            query (str): The query to encode.
        Returns:
            str: The encoded query.
        """
        if self.encode is not None:
            return f"encode({query}, \"{self.encode}\")"
        return query
