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

from s3uploader import api


app = flask.Flask(__name__)
api_blueprint = flask.Blueprint('api', __name__)
api_service = flask_restful.Api(api_blueprint)

api_service.add_resource(api.Asset, '/asset/<string:asset_id>')
api_service.add_resource(api.Assets, '/asset')
app.register_blueprint(api_blueprint)


def main():
    app.run(debug=False)
