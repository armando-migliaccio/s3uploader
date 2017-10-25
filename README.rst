===========
S3 Uploader
===========

A simple S3 uploader.

To execute the API service run the following command. Before doing that,
remember to export the environment variables ``AWS_ACCESS_KEY_ID``,
``AWS_SECRET_ACCESS_KEY``, ``AWS_REGION``.

``tox -evenv api``

Then you can hit it with basic requests such as:

``curl http://localhost:5000/asset  -X POST``

You run basic unit testing by doing (depending on your Python runtime):

``tox -epy35``

You can run pep8 validation with:

``tox -epep8``
