# -*- coding: utf-8 -*-
"""
server.py Tests Module

To laught the tests::

    python test_server.py

In verbose mode::

    python test_server.py -v

see http://docs.python.org/2.6/library/doctest.html
"""

import server
import doctest
doctest.testmod(server, report=True)
