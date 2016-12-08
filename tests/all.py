import unittest
import doctest
# import mock

# test the server with doctest
import test_server

# test LDAP
import test_ldap

suite = unittest.TestSuite()

# add doctest files
suite.addTest(doctest.DocTestSuite(test_server))

# add unnittest files
suite.addTest(unittest.TestLoader().loadTestsFromModule(test_ldap))

runner = unittest.TextTestRunner(verbosity=2)
runner.run(suite)





    
