# coding: utf-8

"""
    NoLabs

    No description provided (generated by Openapi Generator https://github.com/openapitools/openapi-generator)

    The version of the OpenAPI document: 1
    Generated by OpenAPI Generator (https://openapi-generator.tech)

    Do not edit the class manually.
"""  # noqa: E501


import unittest
import datetime

from nolabs_microservice.models.rcsb_pdb_data import RcsbPdbData

class TestRcsbPdbData(unittest.TestCase):
    """RcsbPdbData unit test stubs"""

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def make_instance(self, include_optional) -> RcsbPdbData:
        """Test RcsbPdbData
            include_option is a boolean, when False only required
            params are included, when True both required and
            optional params are included """
        # uncomment below to create an instance of `RcsbPdbData`
        """
        model = RcsbPdbData()
        if include_optional:
            return RcsbPdbData(
                content = None,
                metadata = nolabs_microservice.models.rcsb_pdb_meta_data.RcsbPdbMetaData(
                    link = null, )
            )
        else:
            return RcsbPdbData(
                metadata = nolabs_microservice.models.rcsb_pdb_meta_data.RcsbPdbMetaData(
                    link = null, ),
        )
        """

    def testRcsbPdbData(self):
        """Test RcsbPdbData"""
        # inst_req_only = self.make_instance(include_optional=False)
        # inst_req_and_optional = self.make_instance(include_optional=True)

if __name__ == '__main__':
    unittest.main()