# -*- coding: utf-8 -*-

from context import server

import sys
import unittest
from mock import MagicMock as mo
from mock import patch 
# import ldap


class TestLdap(unittest.TestCase):
    """ldap test"""

    def setUp(self):
        import ldap

    def tearDown(self):
        del sys.modules['ldap']

    def test__ldap_uri(self):
        self.assertEqual(server._ldap_uri({}), '')
        self.assertEqual(server._ldap_uri({'host': 'home'}), '')
        self.assertEqual(server._ldap_uri({'name': 'name'}), '')
        self.assertEqual(server._ldap_uri({'host':'home', 'name':'prout'}), 'ldap://home:389')
        self.assertEqual(server._ldap_uri({'host':'home', 'name':'prout', 'port': 1234}), 'ldap://home:1234')

    # @unittest.skip('FIXME camt use mock')
    @patch('ldap.initialize')
    @patch('server._ldap_uri')
    def test__ldap_initialize(self, mock_init, mock_ldap_uri):
        """ test _ldap_initialize"""

        mock_ldap_uri = mo(return_value={'host':'myldap.example.com', 'name': 'myldap'})
        # server._ldap_uri = mock_ldap_uri

        mock_init = mo(return_value=True)
        # server.ldap.initialize = mock_init

        self.assertTrue(server._ldap_initialize({}))
        mock_ldap_uri.assert_called_with({'host':'myldap.example.com', 'name': 'myldap'})
        mock_init.assert_called_with({'host':'myldap.example.com', 'name': 'myldap'})


if __name__ == '__main__':

    # print sys.modules.has_key('ldap')
    unittest.main()
