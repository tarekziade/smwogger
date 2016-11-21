========
Smwogger
========


Smwogger is a smoke test tool and an extension for Swagger.

To add a smoke test for you API, add an **x-smoke-test** section
in your YAML or JSON file, describing your smoke test scenario.

Scenario
========

A scenario is described by providing a sequence of operations to
perform, given their **operationId**.

For each operation, you can make some assertions on the
**response** by providing values for the status code and some
headers.

Example in YAML ::

    x-smoke-test:
      scenario:
      - getSomething:
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
