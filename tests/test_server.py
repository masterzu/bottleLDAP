# -*- coding: utf-8 -*-
"""
server.py Simple Tests Module

To laught the tests::

    python test_server.py

In verbose mode::

    python test_server.py -v

see http://docs.python.org/2.7/library/doctest.html
"""

import doctest

# import my code using config.py
from context import server

doctest.testmod(server, report=True)
