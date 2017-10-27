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

import flask
import flask_restful

from s3uploader import constants
from s3uploader import exceptions
from s3uploader import s3


app = flask.Flask(__name__)
LOG = app.logger


@app.errorhandler(exceptions.AssetError)
def special_exception_handler(error):
    LOG.error(error)
    return 'ouch, something went wrong, please try later!', 500


class Asset(flask_restful.Resource):

    def get(self, asset_id):
        """Return an S3 signed URL for dowload of a given asset.

        :returns: 400 if the timeout is not a positive integer.
        :returns: 404 if the asset cannot be found.
        :returns: 409 if the asset is not ready for download.

        """
        timeout = flask.request.args.get('timeout', constants.DOWNLOAD_TIMEOUT)
        # TODO(armax): could use Flask-inputs but it's more hassle
        # than it's worth for the simplicity of the app.
        try:
            timeout = int(timeout)
            if timeout <= 0:
                raise ValueError()
        except ValueError:
            LOG.error('Timeout cannot be parsed: %s', timeout)
            # TODO(armax): return messages should be localized
            return 'timeout must be a positive integer', 400

        asset_manager = s3.AssetManager()
        asset = asset_manager.get_asset(asset_id, timeout)
        if asset and asset.url:
            return {'download_url': asset.url}
        elif asset and not asset.url:
            return 'asset is not ready for download', 409
        else:
            return 'asset cannot be found', 404

    def put(self, asset_id):
        """Mark an asset upload operation as completed."""
        content = flask.request.get_json(force=True)
        # TODO(armax): could use Flask-inputs but it's more hassle
        # than it's worth for the simplicity of the app.
        if 'Status' not in content:
            # TODO(armax): return messages should be localized
            return 'Body must contain "Status" key', 400
        asset_manager = s3.AssetManager()
        asset_manager.update_asset(asset_id)
        return 'done'


class Assets(flask_restful.Resource):

    def post(self):
        """Return an S3 signed URL for uploading a new asset."""
        s3_signed_url = None
        asset_id = None
        response = {
            'upload_url': s3_signed_url,
            'id': asset_id,
        }
        return response
