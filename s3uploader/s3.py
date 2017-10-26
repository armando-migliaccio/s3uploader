# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

import os
import uuid

import boto3


class Config(object):
    # TODO(armax): make this more sophisticated if need be.
    # or replace in favor of Boto3 default ~/.aws/config
    def __init__(self):
        self.bucket = os.environ['AWS_BUCKET']
        self.access_key_id = os.environ['AWS_ACCESS_KEY_ID']
        self.access_key = os.environ['AWS_SECRET_ACCESS_KEY']
        self.region = os.environ['AWS_REGION']


class Asset(object):

    def __init__(self, url=None, asset_id=None):
        self.url = url
        self.asset_id = asset_id


class AssetManager(object):

    def __init__(self, storage_manager=None):
        self.storage_manager = storage_manager or S3Manager()

    def create_asset(self):
        asset_id = self._generate_uuid()
        url = self.manager.get_url_for_upload(asset_id)
        return Asset(url, asset_id)

    def update_asset(self, asset_id):
        self.manager.update_upload_status(asset_id)

    def get_asset(self, asset_id, timeout):
        url = self.storage_manager.get_url_for_download(asset_id, timeout)
        return Asset(url, asset_id)

    def _generate_uuid(self):
        return str(uuid.uuid4())


class S3Manager(object):

    def __init__(self, config=None):
        self.config = config or Config()
        self.client = boto3.client(
            's3',
            aws_access_key_id=self.config.access_key_id,
            aws_secret_access_key=self.config.access_key,
            region_name=self.config.region)

    def get_url_for_upload(self, asset_id):
        pass

    def update_upload_status(self, asset_id):
        pass

    def get_url_for_download(self, asset_id, timeout):
        return self.client.generate_presigned_url(
            ClientMethod='get_object',
            Params={
                'Bucket': self.config.bucket,
                'Key': asset_id
            },
            ExpiresIn=timeout,
            HttpMethod='GET')
