# coding: utf-8

"""
    Bio Buddy

    No description provided (generated by Openapi Generator https://github.com/openapitools/openapi-generator)

    The version of the OpenAPI document: 0.1.0
    Generated by OpenAPI Generator (https://openapi-generator.tech)

    Do not edit the class manually.
"""  # noqa: E501


import unittest

from biobuddy_microservice.models.send_action_call_request import SendActionCallRequest


class TestSendActionCallRequest(unittest.TestCase):
    """SendActionCallRequest unit test stubs"""

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def make_instance(self, include_optional) -> SendActionCallRequest:
        """Test SendActionCallRequest
        include_option is a boolean, when False only required
        params are included, when True both required and
        optional params are included"""
        # uncomment below to create an instance of `SendActionCallRequest`
        """
        model = SendActionCallRequest()
        if include_optional:
            return SendActionCallRequest(
                action_text = '',
                tools = [
                    None
                    ],
                job_id = None
            )
        else:
            return SendActionCallRequest(
                action_text = '',
                tools = [
                    None
                    ],
        )
        """

    def testSendActionCallRequest(self):
        """Test SendActionCallRequest"""
        # inst_req_only = self.make_instance(include_optional=False)
        # inst_req_and_optional = self.make_instance(include_optional=True)


if __name__ == "__main__":
    unittest.main()
