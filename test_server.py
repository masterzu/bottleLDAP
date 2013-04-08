# -*- coding: utf-8 -*-
"""
server.py Tests Module

To laught the tests:

python -v test_server.py

see http://docs.python.org/2.6/library/doctest.html
"""

import server
import doctest
doctest.testmod(server, verbose=True, report=True)
