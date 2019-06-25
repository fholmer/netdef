========
Overview
========

When you create an application in Netdef, your project folder will get
the following structure:

* Controllers
* Expressions
* Interfaces
* Rules
* Sources

Your application consists of one *engine*, one or more *rules*, one or
more *sources* and one or more *controllers*. The *engine* is an instance
of the ThreadedEngine class, the *rules* are instances of classes that are
inherited from BaseRule, *sources* are instances of classes inherited from
BaseSource, and *controllers* are instances of classes inherited from
BaseController. All instances have their own "inbox" and the instances
communicate with each other by registering a message in the inbox of the
instance to be read message. The most important message types in your
application are ADD_SOURCE, ADD_PARSER, WRITE_SOURCE and RUN_EXPRESSION.

The message flow will in most cases be as follows: *Rules* will
send ADD_SOURCE to *controllers* at startup. *Controllers* will send
RUN_EXPRESSION back to *rules* on data changes. *Rules* will then
collect *expressions* to be evaluated due to the data change and send
RUN_EXPRESSION to the *engine*. If the *expressions* generate data changes a
WRITE_SOURCE message is sent to *controllers*.

The example below shows 4 simultaneous controllers and 2 simultaneous rules:

.. image :: ../_static/overview.png

The main task of the application is to:

* Obtain external data using one or more *controllers*.
* Retrieving values ​​from external data and activating *expressions* that
  evaluate the values.
* Transmitt data based on the result of the *expression*
