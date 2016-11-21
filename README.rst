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

Example in YAML ::

    x-smoke-test:
      scenario:
      - - operation1
        - status: 200
      - - operation2
        - status: 200
      - - operation3
        - status: 200

Variables
=========

When Smwogger builds queries to call the service, it might
need some values in those cases:


- path templating, to replace variable names with actual values
- XXX
- XXX


You can also extract values from the service responses, in order
to reuse them in subsequential operations.

For example, if operation2 returns a JSON dict with a "foo" value,
you can extract it by declaring it in a vars section::

    x-smoke-test:
      scenario:
      - - operation1
        - status: 200
      - - operation2
        - status: 200
          vars:
            foo:
              query: foo
              default: baz
      - - operation3
        - status: 200

Smwogger will use the **query** value to know where to look in the response
body and extract the value. If the value is not found and **default** is
provided, the variable will take that value.

Once the variable is set, it can be reused by Smwogger for subsequent operations.




