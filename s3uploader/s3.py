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
from botocore import exceptions as boto_exc
import flask

from s3uploader import exceptions


app = flask.Flask(__name__)
LOG = app.logger


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
        url = self.storage_manager.get_url_for_upload(asset_id)
        return Asset(url, asset_id)

    def update_asset(self, asset_id):
        self.storage_manager.update_upload_status(asset_id)

    def get_asset(self, asset_id, timeout):
        url = self.storage_manager.get_url_for_download(asset_id, timeout)
        return Asset(url, asset_id)

    def _generate_uuid(self):
        return str(uuid.uuid4())


class S3Manager(object):

    def __init__(self, config=None, client=None):
        self.config = config or Config()
        self.client = client or boto3.client(
            's3',
            aws_access_key_id=self.config.access_key_id,
            aws_secret_access_key=self.config.access_key,
            region_name=self.config.region)

    def get_url_for_upload(self, asset_id):
        """Return data to allow clients to upload an S3 object."""
        # NOTE(armax): presigned POSTs are more convoluted than presigned
        # PUTs, and allow more control over the transfer of the user content
        # to the S3 object. This method of generating the presigned POST is
        # barebone and would allow a web client to post content like this:
        #
        # import requests
        #
        # myfile = {"file": "file_content"}
        # response = requests.post(
        #     post["url"], data=post["fields"], files=myfiles)
        #
        try:
            return self.client.generate_presigned_post(
                Bucket=self.config.bucket,
                Key=asset_id)
        except boto_exc.BotoCoreError:
            # FIXME(armax): narrow down the catch
            raise exceptions.AssetError()

    def update_upload_status(self, asset_id):
        """Mark the S3 object's upload completed."""
        try:
            self.client.put_object_tagging(
                Bucket=self.config.bucket,
                Key=asset_id,
                Tagging={
                    'TagSet': [
                        {'Key': 'Status', 'Value': 'Uploaded'}
                    ]
                })
        except boto_exc.ClientError as e:
            LOG.error(e)
            if 'Error' in e.response:
                raise ERROR_MAP.get(e.response['Error']['Code'],
                                    exceptions.AssetError())
                raise exceptions.AssetNotFoundError()
            raise exceptions.AssetError()
        except boto_exc.BotoCoreError as e:
            LOG.error(e)
            raise exceptions.AssetError()

    def get_url_for_download(self, asset_id, timeout):
        """Return URL for download if the asset is ready, None otherwise."""
        try:
            # check if this is marked uploaded
            tags = self.client.get_object_tagging(
                Bucket=self.config.bucket,
                Key=asset_id)
            uploaded = False
            if tags:
                for tag in tags['TagSet']:
                    key = tag.get('Key')
                    value = tag.get('Value')
                    if key == 'Status' and value == 'Uploaded':
                        uploaded = True
                        break
            if not uploaded:
                return

            # if so, then return URL for download
            return self.client.generate_presigned_url(
                ClientMethod='get_object',
                Params={
                    'Bucket': self.config.bucket,
                    'Key': asset_id
                },
                ExpiresIn=timeout,
                HttpMethod='GET')
        except boto_exc.ClientError as e:
            LOG.error(e)
            if 'Error' in e.response:
                raise ERROR_MAP.get(e.response['Error']['Code'],
                                    exceptions.AssetError())
            raise exceptions.AssetError()
        except boto_exc.BotoCoreError as e:
            LOG.error(e)
            raise exceptions.AssetError()


ERROR_MAP = {
    'NoSuchKey': exceptions.AssetNotFoundError,
    'AccessDenied': exceptions.AssetAccessDeniedError
}
