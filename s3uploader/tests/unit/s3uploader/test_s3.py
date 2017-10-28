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

from botocore import exceptions as boto_exc
import mock
import testtools

from s3uploader import exceptions
from s3uploader import s3


class TestAssetManager(testtools.TestCase):

    def setUp(self):
        super(TestAssetManager, self).setUp()
        self.storage_mock = mock.Mock()
        self.manager = s3.AssetManager(storage_manager=self.storage_mock)
        self.addCleanup(mock.patch.stopall)

    def test_create_asset(self):
        self.storage_mock.get_url_for_upload.return_value = 'foo_url'
        asset = self.manager.create_asset()
        self.assertIsNotNone(asset)
        self.assertEqual('foo_url', asset.url)

    def test_update_asset(self):
        self.manager.update_asset('foo_asset_id')
        self.storage_mock.update_upload_status.assert_called_once_with(
            'foo_asset_id')

    def test_get_asset(self):
        self.storage_mock.get_url_for_download.return_value = 'foo_url'
        asset = self.manager.get_asset('foo_asset_id', 50)
        self.assertIsNotNone(asset)
        self.assertEqual('foo_url', asset.url)


class TestS3Manager(testtools.TestCase):

    def setUp(self):
        super(TestS3Manager, self).setUp()
        self.manager = s3.S3Manager(config=mock.Mock(), client=mock.Mock())
        self.addCleanup(mock.patch.stopall)

    def test_get_url_for_upload(self):
        self.manager.get_url_for_upload('foo_asset_id')
        self.manager.client.generate_presigned_post.assert_called_once()

    def test_update_upload_status(self):
        self.manager.update_upload_status('foo_asset_id')
        self.manager.client.put_object_tagging.assert_called_once()

    def test_update_upload_status_raise_not_found(self):
        exc = boto_exc.ClientError(
            error_response={}, operation_name='foo')
        exc.response['Error'] = {'Code': 'NoSuchKey'}
        self.manager.client.put_object_tagging.side_effect = exc
        self.assertRaises(
            exceptions.AssetNotFoundError,
            self.manager.update_upload_status, 'foo_asset_id')

    def test_get_url_for_download_ready_for_download(self):
        self.manager.client.get_object_tagging.return_value = (
            {'TagSet': [{'Key': 'Status', 'Value': 'Uploaded'}]})

        self.manager.get_url_for_download('foo_asset_id', 50)
        self.manager.client.get_object_tagging.assert_called_once()
        self.manager.client.generate_presigned_url.assert_called_once()

    def test_get_url_for_download_not_ready_for_download(self):
        self.manager.client.get_object_tagging.return_value = None

        self.manager.get_url_for_download('foo_asset_id', 50)
        self.manager.client.get_object_tagging.assert_called_once()
        self.assertFalse(self.manager.client.generate_presigned_url.call_count)

    def test_get_url_for_download_not_found(self):
        exc = boto_exc.ClientError(
            error_response={}, operation_name='foo')
        exc.response['Error'] = {'Code': 'NoSuchKey'}
        self.manager.client.get_object_tagging.side_effect = exc
        self.assertRaises(
            exceptions.AssetNotFoundError,
            self.manager.get_url_for_download, 'foo_asset_id', 50)

    def test_get_url_for_download_unknown_error(self):
        exc = boto_exc.ClientError(
            error_response={}, operation_name='foo')
        exc.response['Error'] = {'Code': 'UncaughtError'}
        self.manager.client.get_object_tagging.side_effect = exc
        self.assertRaises(
            exceptions.AssetError,
            self.manager.get_url_for_download, 'foo_asset_id', 50)

    def test_get_url_for_upload_raises(self):
        self.manager.client.generate_presigned_post.side_effect = (
            boto_exc.BotoCoreError)
        self.assertRaises(exceptions.AssetError,
                          self.manager.get_url_for_upload, 'foo_asset_id')

    def test_update_upload_status_raises(self):
        self.manager.client.put_object_tagging.side_effect = (
            boto_exc.ClientError(error_response={}, operation_name='foo'))
        self.assertRaises(exceptions.AssetError,
                          self.manager.update_upload_status, 'foo_asset_id')
