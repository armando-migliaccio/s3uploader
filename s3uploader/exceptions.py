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

from werkzeug import exceptions


class AssetError(exceptions.HTTPException):
    code = 500
    description = 'ouch, something went wrong, please try later'

    def __init__(self):
        super(AssetError, self).__init__()


class AssetNotFoundError(exceptions.HTTPException):
    code = 404
    description = 'asset cannot be found, check asset ID'

    def __init__(self):
        super(AssetNotFoundError, self).__init__()


class AssetAccessDeniedError(exceptions.HTTPException):
    code = 401
    description = 'asset cannot be accessed, check permissions'

    def __init__(self):
        super(AssetAccessDeniedError, self).__init__()
