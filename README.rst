===========
S3 Uploader
===========

A simple S3 uploader written in Python.

Getting started
===============

System dependencies
-------------------

Being this a Python app, your machine must have a Python interpreter
(2.x or 3.x) and have the necessary dependencies to run the project in
a virtualenv.

AWS dependencies
----------------

The S3 uploader interfaces with...S3. For that reason, make sure you know
how to provision your AWS credentials to be able to have the asset uploader
to talk to S3. It is important that the credentials used to access S3 have
enough permissions to allow the S3 uploader to work correctly. As the S3
uploader uses tagging to mark assets available for download (to avoid
depending on external storage), ensure that the following policies are
allowed: GetObjectTagging, PutObjectTagging.

Kicking the tires
-----------------

To execute the API service in a test environment, you can use tox. Before
doing that, remember to export the environment variables:

 * ``AWS_BUCKET``
 * ``AWS_ACCESS_KEY_ID``
 * ``AWS_SECRET_ACCESS_KEY``
 * ``AWS_REGION``

To run the service, execute the following command:

``tox -evenv service``

Then you can hit it with basic requests such as:

``curl http://localhost:5000/asset -X POST``

You run basic unit testing by doing (depending on your Python runtime):

``tox -epy35``

You can run pep8 validation with:

``tox -epep8``

You can unit test coverage with:

``tox -ecover``

To look for potential security issues, run:

``tox -ebandit``


Deployment considerations
-------------------------

To deploy in production, check out:

``http://flask.pocoo.org/docs/0.12/deploying/``

For more details on multiprocessing and threading considerations, please read the
`modwsgi guide <http://modwsgi.readthedocs.io/en/develop/user-guides/processes-and-threading.html>`_.
