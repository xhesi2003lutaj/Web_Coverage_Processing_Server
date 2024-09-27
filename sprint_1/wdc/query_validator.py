# import re
#
# class QueryValidator:
#     " validator class to check queries"
#
#     def __init__(self):
#         self.coverage_pattern = r"^\w+$" 
#         self.axis_pattern = r"^\w+\((\d+:\d+)\)$"  # Format (start:end)
#
#     def validate_query(self, query):
#         if not query or " " in query:
#             raise ValueError("Query must not contain spaces")
#
#     def validate_coverage_name(self, coverage_name):
#         if not re.match(self.coverage_pattern, coverage_name):
#             raise ValueError(f"Invalid coverage naming {coverage_name}")
#
#     def validate_axis_range(self, axis_range):
#         if not re.match(self.axis_pattern, axis_range):
#             raise ValueError(f"Invalid range format: {axis_range}")
#
#
# if __name__ == "__main__":
#     validator = QueryValidator()
#     try:
#         validator.validate_query("correct_query")
#         validator.validate_coverage_name("Coverage123")
#         validator.validate_axis_range("time(0:10)")
#         print("Validation passed!")
#     except ValueError as e:
#         print(f"Validation error: {e}")
