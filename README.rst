========
Smwogger
========

.. image:: http://coveralls.io/repos/github/tarekziade/smwogger/badge.svg?branch=master
   :target: https://coveralls.io/github/tarekziade/smwogger?branch=master

.. image:: http://travis-ci.org/tarekziade/smwogger.svg?branch=master
   :target: https://travis-ci.org/tarekziade/smwogger



**Smwogger** (pronounced smoger) is a smoke test tool for Swagger.

Smwogger's goal is to provide a quick and simple way to smoke
test a deployment.

To add a smoke test for you API, you have three options:

1. Add an **x-smoke-test** section in your Swagger spec, describing your
   smoke test scenario.
2. Have a specific file that contains the **x-smoke-test** section.
3. Use the API class which binds its methods to Swagger operations


Example using x-smoke-test
==========================

You can run the test by pointing the Swagger spec URL (or path to a file)::

    $ smwogger smwogger/tests/shavar.yaml
    Scanning spec... OK

            This is project 'Shavar Service'
            Mozilla's implementation of the Safe Browsing protocol
            Version 0.7.0


    Running Scenario
    1:getHeartbeat... OK
    2:getDownloads... OK
    3:getDownloads... OK

If you need to get details about the requests and responses sent, you can
use the **-v** option::

    $ smwogger -v smwogger/tests/shavar.yaml
    Scanning spec... OK

            This is project 'Shavar Service'
            Mozilla's implementation of the Safe Browsing protocol
            Version 0.7.0


    Running Scenario
    1:getHeartbeat...
    GET https://shavar.somwehere.com/__heartbeat__
    >>>
    HTTP/1.1 200 OK
    Content-Type: text/plain; charset=UTF-8
    Date: Mon, 21 Nov 2016 14:03:19 GMT
    Content-Length: 2
    Connection: keep-alive

    OK
    <<<
    OK
    2:getDownloads...
    POST https://shavar.somwehere.com/downloads
    Content-Length: 30

    moztestpub-track-digest256;a:1

    >>>
    HTTP/1.1 200 OK
    Content-Type: application/octet-stream
    Date: Mon, 21 Nov 2016 14:03:23 GMT
    Content-Length: 118
    Connection: keep-alive

    n:3600
    i:moztestpub-track-digest256
    ad:1
    u:tracking-protection.somwehere.com/moztestpub-track-digest256/1469223014

    <<<
    OK
    3:getDownloads...
    POST https://shavar.somwehere.com/downloads
    Content-Length: 35

    moztestpub-trackwhite-digest256;a:1

    >>>
    HTTP/1.1 200 OK
    Content-Type: application/octet-stream
    Date: Mon, 21 Nov 2016 14:03:23 GMT
    Content-Length: 128
    Connection: keep-alive

    n:3600
    i:moztestpub-trackwhite-digest256
    ad:1
    u:tracking-protection.somwehere.com/moztestpub-trackwhite-digest256/1469551567

    <<<
    OK


Describing your scenario
========================

A scenario is described by providing a sequence of operations to
perform, given their **operationId**.

For each operation, you can make some assertions on the
**response** by providing values for the status code and some
headers.

Example in YAML ::

    x-smoke-test:
      scenario:
      - getSomething:
          request:
            params:
              foo: bar
          response:
            status: 200
            headers:
              Content-Type: application/json
      - getSomethingElse
          response:
            status: 200
      - getSomething
          response:
            status: 200

If a response does not match, an assertion error will be raised.


Posting data
============

When you are posting data, you can provide the request body content in the
operation under the **request** key.

Example in YAML ::

    x-smoke-test:
      scenario:
      - postSomething:
          request:
            body: This is the body I am sending.
          response:
            status: 200


Replacing Path variables
========================

If some of your paths are using template variables, as defined by the swagger
spec, you can use the **path** option::


    x-smoke-test:
      scenario:
      - postSomething:
          request:
            body: This is the body I am sending.
            path:
              var1: ok
              var2: blah
          response:
            status: 200

You can also define global path values that will be looked up when formatting
paths. In that case, variables have to be defined in a top-level **path**
section::

    x-smoke-test:
      path:
        var1: ok
      scenario:
      - postSomething:
          request:
            body: This is the body I am sending.
            path:
              var2: blah
          response:
            status: 200


Variables
=========

You can extract values from responses, in order to reuse them in
subsequential operations, wether it's to replace variables in
path templates, or create a body.

For example, if **getSomething** returns a JSON dict with a "foo" value,
you can extract it by declaring it in a **vars** section inside the
**response** key::

    x-smoke-test:
      path:
        var1: ok
      scenario:
      - getSomething:
          request:
            body: This is the body I am sending.
            path:
              var2: blah
          response:
            status: 200
            vars:
              foo:
                query: foo
                default: baz

Smwogger will use the **query** value to know where to look in the response
body and extract the value. If the value is not found and **default** is
provided, the variable will take that value.

Once the variable is set, it will be reused by Smwogger for subsequent
operations, to replace variables in path templates, or to fill response data.

The path formatting is done automatically. Smwogger will look first at
variables defined in operations, then at the path sections.

If you want to use a variable in a body, you need to use the ${formatting}::

    x-smoke-test:
      path:
        var1: ok
      scenario:
      - getSomething:
          response:
            vars:
              foo:
                query: foo
                default: baz
      - doSomething:
          request:
            body: ${foo}


Using the API
=============


If your scenario is too complex for fitting in the description,
you can use a plain Python script in the --test option.

A Python script test is a module with a **scenario** function.
The function will be executed and will get an instance of the API
class.

Example::

    from smwogger.cli import console

    def scenario(api):
        with console('Getting something'):
            resp = api.getSomething()
        assert resp.status_code == 200



XXX more info here


