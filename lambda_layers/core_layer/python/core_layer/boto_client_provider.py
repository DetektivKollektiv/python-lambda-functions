import os
import boto3


class BotoClientProvider:
    def __init__(self) -> None:
        pass

    def get_client(self, type: str, region: str = "eu-central-1"):
        is_test = os.environ['STAGE'] == 'test'

        if(is_test):
            return boto3.client(type, endpoint_url='http://localhost:4566', region_name=region)

        return boto3.client(type, region_name=region)
