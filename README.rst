================
EPC SunSpec Demo
================

.. image:: https://img.shields.io/github/workflow/status/epcpower/sunspec-demo/CI/main?color=seagreen&logo=GitHub-Actions&logoColor=whitesmoke
   :alt: tests on GitHub Actions
   :target: https://github.com/epcpower/sunspec-demo/actions?query=branch%3Amain

.. image:: https://img.shields.io/github/last-commit/epcpower/sunspec-demo/main.svg
   :alt: source on GitHub
   :target: https://github.com/epcpower/sunspec-demo

The EPC SunSpec demo implements basic SunSpec communications with EPC converters.
SunSpec is built on Modbus and works with both Modbus RTU (direct serial) and Modbus TCP connections.
Additionally this program acts as a basic example of using the `pysunspec`_ Python library.

.. _pysunspec: https://github.com/sunspec/pysunspec


------------
Installation
------------

The ``poetry`` & ``poetry-dynamic-versioning`` packages must be installed.

::

    pip install poetry
    pip install poetry-dynamic-versioning

Windows & Linux
===============

::

    poetry install
    poetry run sunspecdemo get-models


-------
Running
-------

A list of commands and options will be reported if ``--help`` is passed.
This can be done at any layer in the tree of subcommands.
When options provide defaults they will be listed in the help output.


``get-models``
==============

``get-models`` will download the EPC custom models needed for our specific features.


``list-ports``
==============

As an aid to selecting the proper serial port this subcommand will report a list of those available.
In some cases extra identifying information may be provided as well.


``scan``
========

Scan for responding nodes in a given node ID range.
Provides both direct ``serial`` and ``tcp`` subcommands


``gridtied``, ``dcdc``
=========================

Converters can be run over either Modbus RTU or Modbus TCP.
A subcommand is provided for each: ``serial`` and ``tcp``.
When running a fully selected command a basic demo sequence will be run to confirm communication with the device.


``serial``
----------

For a Modbus RTU connection to the converter.
At a minimum the serial port connected to the converter must be specified.


``tcp``
-------

For a Modbus TCP connection to the converter.
At a minimum the IP address or hostname of the converter must be specified.
