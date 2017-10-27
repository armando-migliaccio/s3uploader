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

import mock
from oslo_serialization import jsonutils
import testtools

from s3uploader.cmds.service import app
from s3uploader import exceptions
from s3uploader import s3


class TestS3Uploader(testtools.TestCase):

    def setUp(self):
        super(TestS3Uploader, self).setUp()
        self.app = app.test_client()
        self.manager_patch = mock.patch(
            's3uploader.s3.AssetManager', autospec=True).start()
        self.manager = self.manager_patch.return_value
        self.addCleanup(mock.patch.stopall)

    def test_asset_post(self):
        response = self.app.post('/asset')
        self.assertEqual(response.status_code, 200)
        response_body = jsonutils.loads(response.get_data())
        self.assertIn('upload_url', response_body)
        self.assertIn('id', response_body)

    def test_asset_put(self):
        response = self.app.put('/asset/foo123',
                                data=jsonutils.dumps(dict(Status='uploaded')))
        self.assertEqual(response.status_code, 200)

    def test_asset_get(self):
        self.manager.get_asset.return_value = s3.Asset('foo_url')
        response = self.app.get('/asset/foo123')
        self.assertEqual(response.status_code, 200)
        response_body = jsonutils.loads(response.get_data())
        self.assertIn('download_url', response_body)

    def test_asset_get_not_ready(self):
        self.manager.get_asset.return_value = s3.Asset(None)
        response = self.app.get('/asset/foo123')
        self.assertEqual(response.status_code, 409)

    def test_asset_get_not_found(self):
        self.manager.get_asset.return_value = None
        response = self.app.get('/asset/foo123')
        self.assertEqual(response.status_code, 404)

    def test_asset_get_backend_failure(self):
        self.manager.get_asset.side_effect = exceptions.AssetError()
        response = self.app.get('/asset/foo123')
        self.assertEqual(response.status_code, 500)

    def test_asset_put_backend_failure(self):
        self.manager.update_asset.side_effect = exceptions.AssetError()
        response = self.app.put('/asset/foo123',
                                data=jsonutils.dumps(dict(Status='uploaded')))
        self.assertEqual(response.status_code, 500)


class TestS3UploaderNegativeInputs(testtools.TestCase):

    def setUp(self):
        super(TestS3UploaderNegativeInputs, self).setUp()
        self.app = app.test_client()

    def test_asset_post_wrong_prefix(self):
        response = self.app.post('/asset1')
        self.assertEqual(response.status_code, 404)

    def test_asset_put_bad_input(self):
        response = self.app.put('/asset/foo123',
                                data=jsonutils.dumps(dict(Stotus='uploaded')))
        self.assertEqual(response.status_code, 400)

    def test_asset_get_invalid_timeout(self):
        response = self.app.get('/asset/foo123?timeout=0')
        self.assertEqual(response.status_code, 400)
