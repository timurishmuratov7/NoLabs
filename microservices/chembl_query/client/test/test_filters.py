# coding: utf-8

"""
    ChemBL Query API

    No description provided (generated by Openapi Generator https://github.com/openapitools/openapi-generator)

    The version of the OpenAPI document: 0.1.0
    Generated by OpenAPI Generator (https://openapi-generator.tech)

    Do not edit the class manually.
"""  # noqa: E501


import unittest

from chembl_query_microservice.models.filters import Filters

class TestFilters(unittest.TestCase):
    """Filters unit test stubs"""

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def make_instance(self, include_optional) -> Filters:
        """Test Filters
            include_option is a boolean, when False only required
            params are included, when True both required and
            optional params are included """
        # uncomment below to create an instance of `Filters`
        """
        model = Filters()
        if include_optional:
            return Filters(
            )
        else:
            return Filters(
        )
        """

    def testFilters(self):
        """Test Filters"""
        # inst_req_only = self.make_instance(include_optional=False)
        # inst_req_and_optional = self.make_instance(include_optional=True)

if __name__ == '__main__':
    unittest.main()