*****************
Development notes
*****************

.. contents:: Table of Contents
   :depth: 2

.. |--| unicode:: U+02013 .. en dash

git Source workflow
===================

Use the `gitflow workflow <http://nvie.com/posts/a-successful-git-branching-model/>`_ with 2 main branches: **master** for the production code and **develop** for the current devel code.

Developpment Requirement
========================

Tools for client side
---------------------

I use `grunt <http://gruntjs.com/>`_ and `bower <https://bower.io/>`_ to import all javascript libraries

* install ``npm``. ``npm`` is part of `nodejs <https://nodejs.org/en/download/>`_ project.
* install commands ``grunt``, ``bower`` and ``phantomjs`` ::
    
    $ npm install -g grunt-cli bower phantomjs

* install grunt libraries listed in *package.json*::

    $ npm install

* install all javascript libraries listed in *bower.json*::

    $ bower install 

Tools for server side devel
---------------------------

* (optional) install **virtualenv** to have separated python environment from OS host

* install python modules listed in *requirements.txt* and *requirements_devel.txt*::

  $ pip install -r requirements.txt 
  $ pip install -r requirements_devel.txt

Go to release
=============

Before release, you **must** have a clean repository.

#. Launch ./make_release.sh with the *good* version ie ``x.y.z``::

   make_release.sh 0.17.0

#. If no error occurs, follow the script steps:

   #. commit

   #. pass to master branch

   #. merge and resolve merges (``git mergetool`` may help)

   #. commit

   #. tag

Python modules notes
====================

Modules uses by de application (see requirements.txt for details):

* bottle
* ldap
* pymongo
* paramiko

Modules uses to help develop the application:

* autopep8 |--| to check and clean de Python code
* Pygments |--| to views sources in the commandline

Using virtualenv, I can change the production/development environment to add required modules.

paramiko
--------

warning issue
_____________

The old [*]_ **paramiko** module, to use ssh in python use an old **pycrypto** function with the **warning**: ``RandomPool_DeprecationWarning`` 
Since ``2.0`` **pycrypto** was replace by the module **Cryptography**.

.. [*] the devel computer is on Debian 6, with paramiko ``1.7.6``.

This issue can be fixed with a recent version of **pycrypto** On pypi, only the version ``2.6`` is available.

Speed issue
___________


.. note:: With paramiko 2.3.x the speed and security issues are over.

With the last tested [*]_ of **paramiko** and **pycrypto**/**cryptography** in last version, the all process is very slow. 
(See tables below)

:Conclusion: To have optimal speed I use **paramiko** ``1.10.0`` and **pycrypto** ``2.6.1`` (in pip version)


.. [*] last test is for paramiko ``2.0.2``

To fix this, I use in production the python environment **Debian 6.0 + virtualenv --site-package**
without upgrading **paramiko**.

All tables of measurements.

========= ========= ========== =========== =================
 paramiko version with OS version + virtualenv --site-package
------------------------------------------------------------
 version   warning   ssh_init  ssh_connect ssh_commands (uname)  
========= ========= ========== =========== =================
 with pycrypto ``2.1.0`` (debian 6 version)
------------------------------------------------------------
1.7.6        X      0.01s      0.20s       0.04s            
 with pycrypto ``2.6`` (pip version)
------------------------------------------------------------
1.7.6        X      0.01s      **1.39s**       0.04s            
 (new tests on Debian 8) with pycrypto ``2.6.1`` and cryptography ``0.6.1``
------------------------------------------------------------
1.15.1              **0.43s**      0.15s       0.04s
========= ========= ========== =========== =================

========= ========= ========== =========== =================
 paramiko version with ``virtualenv --no-site-package`` 
------------------------------------------------------------
 version   warning   ssh_init  ssh_connect ssh_commands (uname)  
========= ========= ========== =========== =================
 (pycrypto version is always the last : ``2.6``)
------------------------------------------------------------
1.7.4        X      0.01s      **1.39s**       0.04s            
1.7.5        X      0.01s      1.39s       0.05s            
1.7.6        X      0.01s      1.38s       0.04s            
1.7.7.1             0.01s      1.38s       0.15s            
1.7.7.2             0.01s      1.38s       0.05s            
1.8.0               0.01s      1.39s       0.04s            
1.8.1               0.01s      1.39s       0.04s            
1.9.0               0.01s      1.39s       0.04s            
1.10.0              0.01s      1.39s       0.04s            
1.10.1              0.01s      1.39s       0.04s            
1.10.2              0.01s      1.39s       0.04s            
1.10.3              0.01s      1.38s       0.04s            
1.11.0              0.01s      1.38s       0.04s            
1.11.1              0.01s      1.38s       0.04s            
========= ========= ========== =========== =================

========= ========= ========== =========== ================= =====
 paramiko version with ``virtualenv --no-site-package`` 
------------------------------------------------------------------
 version   warning   ssh_init  ssh_connect ssh_commands      total
========= ========= ========== =========== ================= =====
 (new tests with pycrypto ``2.6.1``)
------------------------------------------------------------------
1.7.6               0.02s      0.14s       0.00s             0.16s
1.7.7.1             0.02s      0.14s       0.00s             0.16s
1.8.8               0.02s      0.14s       0.00s             0.16s
1.9.0               0.02s      0.14s       0.00s             0.16s
1.10.0              0.02s      0.14s       0.00s             0.16s
1.11.0              0.09s      0.14s       0.00s             0.23s
1.12.0              **5.36s**      0.14s       0.00s             5.51s
1.13.0              5.68s      0.14s       0.00s             5.84s
1.14.0              5.54s      0.14s       0.00s             5.68s
1.15.0              0.44s      0.15s       0.00s             0.58s
1.16.0              0.43s      0.15s       0.00s             0.58s
1.17.0              0.44s      0.15s       0.00s             0.58s
2.0.0        X      0.12s      0.13s       0.00s             0.26s
2.1.0        X      0.11s      0.13s       0.00s             0.25s
2.2.0        X      0.11s      0.20s       0.01s             0.33s
2.3.0               0.12s      0.19s       0.01s             0.32s
2.4.0               0.12s      0.21s       0.01s             0.34s
 (new tests with cryptography ``1.5``)
------------------------------------------------------------------
2.0.0               0.56s      0.14s       0.00s             0.71s
2.0.1               0.55s      0.14s       0.00s             0.71s
2.0.2               0.56s      0.14s       0.00s             0.71s
========= ========= ========== =========== ================= =====

The source is::

    import paramiko
    try:
        import Crypto
    except:
        pass
    try:
        import cryptography
    except:
        pass

    import os



    # timeit decorator
    def timeit(method):
        """
        From « A Python decorator for measuring the execution time of methods », 
        Andeas Jung, Sep 17 2009
        http://urlalacon.com/TxzcFy
        
        Uses:
        @_timeit
        def my_fonc_to_time
        """
        import time

        def timed(*args, **kw):
            ts = time.time()
            result = method(*args, **kw)
            te = time.time()

            times.append((method.__name__,te-ts))
            return result

        return timed

    @timeit
    def ssh_init():
        ### client SSH
        ssh = paramiko.SSHClient()

        ### known_hosts
        ssh.load_system_host_keys()
        ssh.load_host_keys(os.path.expanduser('~/.ssh/known_hosts'))

        return ssh

    @timeit
    def ssh_connect(ssh, host):
        ### connection
        ssh.connect(host, username='root', password=''
        	, key_filename=os.path.expanduser('id_rsa') )

    def ssh_commands(ssh, list_cmds):
        ### commands
        list_out = []
        
        @timeit
        def _ssh(cmd):
            return ssh.exec_command(cmd)

        for cmd in list_cmds:
            stdin, stdout, stderr = _ssh(cmd)

            # rstripe \n on stdout
            out = ''
            if stdout:
                for o in stdout.readlines():
                    if o.endswith('\n'):
                        o = o[:-1]
                    out = out + o
            else:
                out = '+rien+'


            err = stderr.read()
            if err:
                out += '[err: %s]' % err

            list_out.append((cmd,out))

        return list_out


    def print_long(cmds, times):
        print '-------------------'
        print "Module paramiko %s" % paramiko.__version__
        try:
            print "Module pycrypto %s" % Crypto.__version__
        except:
            pass
        try:
            print "Module cryptography %s" % cryptography.__version__
        except:
            pass
        print '-------------------'
        print ''

        print '-- Commands -------' 
        for c in cmds:
            print "$ %s\n%s" % c
            print

        print '-- Times ----------'
        for obj in times:
            print "%s: %.2f" % obj

        def _p2(acc, v):
            return acc + v[1]

        print '-- Total = %.2fs' % reduce(_p2, times, 0) 

    def print_short(cmds, times):
        def _p(t): 
            return "%.2fs" % t[1]
        def _p2(acc, v):
            return acc + v[1]

        print "paramiko(%s)" % paramiko.__version__,
        try:
            print "pycrypto(%s)" % Crypto.__version__,
        except:
            pass
        try:
            print "cryptography(%s)" % cryptography.__version__
        except:
            pass
        for c  in cmds:
            print "$ %s: %s" % c
        print
        print ' '.join(map(_p, times)),
        print '= %.2fs' % reduce(_p2, times, 0) 



    # main 

    times = []
    c = ssh_init()
    ssh_connect(c,'olympe')
    out = ssh_commands(c, ['uname'])
    c.close()

    #print_long(out, times)
    print_short(out, times)

ldap
----

The module **SimplePagedResultsControl** (RFC 2696) controlling the ``sizelimit`` parameter don't work with the server **openldap**.

The only solution, if you see error like ``SIZELIMIT_EXCEEDED``, is to set a bigger limit to `slapd.conf` (default is 500)::

	sizelimit 1000


Code Style
==========

Try to follow the right path : *Python Enhancement Proposals*.

pep8
----

`Python Enhancement Proposals number 8 <https://www.python.org/dev/peps/pep-0008/>`_, gives coding conventions for the Python code comprising the standard library in the main Python distribution.

In this project I use two tools in this purpose : ``pep8`` and ``autopep8``.

This first, inform the developer about the code and the second can correct it.

The typical process is:

#. get all warning and errors::

    $ pep8 -qq --statistics server.py
    9       E101 indentation contains mixed spaces and tabs
    2       E113 unexpected indentation
    1       E121 continuation line under-indented for hanging indent
    1       E125 continuation line with same indent as next logical line
    1       E129 visually indented line with same indent as next logical line
    3       E203 whitespace before ':'
    4       E225 missing whitespace around operator
    1       E231 missing whitespace after ','
    177     E265 block comment should start with '# '
    1       E301 expected 1 blank line, found 0
    74      E302 expected 2 blank lines, found 1
    21      E303 too many blank lines (3)
    1       E401 multiple imports on one line
    17      E501 line too long (80 > 79 characters)
    4       E701 multiple statements on one line (colon)
    5       W191 indentation contains tabs

#. show source with an error::

    $ pep8 --select=E265 --show-source server.py|less
    server.py:32:1: E265 block comment should start with '# '
    ### standard libraries
    ^
    server.py:42:1: E265 block comment should start with '# '
    ### external libraries
    ^
    server.py:210:1: E265 block comment should start with '# '
    #+ fields:
    ^
#. show source diff, in color, with corrected source::

    $ autopep8 --select=E265 -d server.py |colordiff |less -r

#. correct (or not) this error::

    $ autopep8 --select=E265 -i -j10 server.py

#. (repeat from step 2)

.. :vim:set spell spelllang=en:set ft=rst:
