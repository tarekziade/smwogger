========
Smwogger
========


Smwogger is a smoke test tool and an extension for Swagger.

To add a smoke test for you API, add an **x-smoke-test** section
in your YAML or JSON file, describing your smoke test scenario.

Scenario
========

A scenario is described by providing a list of operations to
perform, given their operation Ids.

For each operation, you can provide a status code.

Smwogger will play the sequence and control the status code
for each operation.

You can also control some headers by defining their names
and values in a headers section.

Example in YAML ::

    x-smoke-test:
      scenario:
      - - getSomething
        - status: 200
          headers:
            Content-Type: application/json
      - - getSomethingElse
        - status: 200
      - - getSomething
        - status: 200

Posting data
============

When you are posting data, you can provide the request body content in the
operation.

Example in YAML ::

    x-smoke-test:
      scenario:
      - - getSomething
        - status: 200
      - - postSomething
        - status: 200
          body: This is the body I am sending.
      - - getSomething
        - status: 200


Replacing Path variables
========================

If some of your paths are using template variables, as defined by the swagger
spec, you can use the **path** option::

    x-smoke-test:
      scenario:
      - - postSomething
        - status: 200
          body: This is the body I am sending.
          path:
            var1: ok
            var2: blah

You can also define global path variables that will be looked up in all operations.
In that case, variables have to be defined in a top-level **path** section::

    x-smoke-test:
      path:
        var1: ok
      scenario:
      - - postSomething
        - status: 200
          body: This is the body I am sending.
          path:
            var2: blah


Variables
=========

You can extract values from responses, in order to reuse them in
subsequential operations, wether it's to replace variables in
path templates, or create a body.

For example, if **getSomething** returns a JSON dict with a "foo" value,
you can extract it by declaring it in a vars section::

    x-smoke-test:
      scenario:
      - - getSomething
        - status: 200
          vars:
            foo:
              query: foo
              default: baz
      - - getSomething
        - status: 200

Smwogger will use the **query** value to know where to look in the response
body and extract the value. If the value is not found and **default** is
provided, the variable will take that value.

Once the variable is set, it will be reused by Smwogger for subsequent
operations, to replace variables in path templates, or to fill response data.

The path formatting is done automatically. Smwogger will look first at
variables defined in operations, then at the path sections.

If you want to use a variable in a body, you need to use the ${formatting}::

    x-smoke-test:
      scenario:
      - - getSomething
        - status: 200
          vars:
            foo:
              query: foo
              default: baz
      - - getSomething
        - status: 200
          body: ${foo}
