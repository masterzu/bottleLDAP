*****************
Development notes
*****************

.. note:: This document is just working notes

git
===

Use the `gitflow workflow <http://nvie.com/posts/a-successful-git-branching-model/>`_ with 2 main branches: **master** for the production code and **develop** for the current devel code.

python and modules
==================

Module uses:

* bottle
* ldap
* pymongo
* paramiko (old version with pycryto ``2.1``)(see below)

Using virtualenv, I change the production environment to add required modules.

paramiko
--------

With those two issue, I use paramoki the an old version of pycrypto to preserve the server speed.

warning issue
_____________

The default [*]_ paramiko module to use ssh in python use an old pycrypto function with the **warning**: ``RandomPool_DeprecationWarning``. 

.. [*] the devel computer is on Debian 6, with paramiko 1.7.6.

This issue can be fixed with a recent version of pycrypto. On pypi, only the version ``2.6`` is available.

Speed issue
___________

With the last version of **paramiko** and **pycrypto**, the function ``paramiko,SSHclient.connect`` is very slow. 
See tables below.

To fix this, I use in production the python environment **Debian 6.0 + virtualenv --site-package**
without upgrading **paramiko**.

All tables of measurements.

========= ========= ========== =========== =================
 paramiko version with Debian 6.0
------------------------------------------------------------
 version   warning   ssh_init  ssh_connect ssh_commands (uname)  
========= ========= ========== =========== =================
1.7.6        X      0.01s      0.20s       0.04s            
========= ========= ========== =========== =================

========= ========= ========== =========== =================
 paramiko version with Debian 6.0 + virtualenv --site-package
------------------------------------------------------------
 version   warning   ssh_init  ssh_connect ssh_commands (uname)  
========= ========= ========== =========== =================
 with pycrypto 2.1.0 (deb version)
------------------------------------------------------------
1.7.6        X      0.01s      0.20s       0.04s            
 with pycrypto 2.6 (pip version)
------------------------------------------------------------
1.7.6        X      0.01s      1.39s       0.04s            
========= ========= ========== =========== =================

========= ========= ========== =========== =================
 paramiko version with ``virtualenv --no-site-package`` 
------------------------------------------------------------
 version   warning   ssh_init  ssh_connect ssh_commands (uname)  
========= ========= ========== =========== =================
 (pycrypto version is always the last : ``2.6``)
------------------------------------------------------------
1.7.4        X      0.01s      1.39s       0.04s            
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

The source is::

    import paramiko, Crypto
    import os

    # timeit decorator
    def timeit(method):
        """
        A Python decorator for measuring the execution time of methods
        from http://www.andreas-jung.com/contents/a-python-decorator-for-measuring-the-execution-time-of-methods
        
        Uses:
        @_timeit
        def my_fonc_to_time
        """
        import time

        def timed(*args, **kw):
            ts = time.time()
            result = method(*args, **kw)
            te = time.time()

            print '%r (%r, %r) %2.2f sec' % (method.__name__, args, kw, te-ts)
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
        ssh.connect(host, username='root', password='', key_filename=os.path.expanduser('id_rsa') )

    @timeit
    def ssh_commands(ssh, list_cmds):
        ### commands
        list_out = []
        for cmd in list_cmds:
            stdin, stdout, stderr = ssh.exec_command(cmd)
            err = stderr.read()
            if err:
                raise SSH_EXEC_ERROR(err)
            else:
                pass

            # rstripe \n on stdout
            for o in stdout.readlines():
                if o.endswith('\n'):
                    o = o[:-1]
                list_out.append(o)

        return list_out


    print '-------------------'
    print "Module paramiko %s" % paramiko.__version__
    print "Module pycrypto %s" % Crypto.__version__
    print '-------------------'
    print ''
    c = ssh_init()
    ssh_connect(c,'olympe')
    ssh_commands(c, ['uname'])

    c.close()
