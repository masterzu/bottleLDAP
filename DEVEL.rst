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

The old [*]_ paramiko module to use ssh in python use an old pycrypto function with the **warning**: ``RandomPool_DeprecationWarning``. 
Since 2.0 pycrypto was replace by the module **Cryptography**.

.. [*] the devel computer is on Debian 6, with paramiko 1.7.6.

This issue can be fixed with a recent version of pycrypto. On pypi, only the version ``2.6`` is available.

Speed issue
___________

With the last tested [*]_ of **paramiko** and **pycrypto**/**cryptography** in last version, the all process is very slow. 
(See tables below)

:Conclusion:To have optimal speed I use **paramiko** 1.10.0 and **pycrypto** 2.6.1 (in pip version)

.. [*] last test is for paramiko 2.0.2

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
 paramiko version with OS version + virtualenv --site-package
------------------------------------------------------------
 version   warning   ssh_init  ssh_connect ssh_commands (uname)  
========= ========= ========== =========== =================
 with pycrypto 2.1.0 (debian 6 version)
------------------------------------------------------------
1.7.6        X      0.01s      0.20s       0.04s            
 with pycrypto 2.6 (pip version)
------------------------------------------------------------
1.7.6        X      0.01s      1.39s       0.04s            
 (new tests on Debian 8) with pycrypto 2.6.1 and cryptography 0.6.1
------------------------------------------------------------
1.15.1              0.43s      0.15s       0.04s
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
 (new tests with pycrypto 2.6.1 and cryptography 1.5)
------------------------------------------------------------
1.7.6               0.02s      0.14s       0.05s
1.7.7.1             0.01s      0.14s       0.05s
1.7.7.2             0.01s      0.14s       0.05s
1.8                 0.01s      0.14s       0.04s
1.9.0               0.01s      0.14s       0.04s
1.10.0              0.01s      0.14s       0.01s
1.11.0              0.09s      0.14s       0.04s
1.12.0              5.39s      0.14s       0.04s
1.13.0              5.66s      0.14s       0.04s
1.14.0              5.55s      0.14s       0.04s
1.15.0              0.43s      0.15s       0.04s
1.16.0              0.43s      0.14s       0.04s
1.17.0              0.43s      0.14s       0.04s
1.17.1              0.43s      0.14s       0.04s
1.17.1              0.43s      0.14s       0.04s
2.0.0               0.54s      0.14s       0.04s
2.0.1               0.55s      0.14s       0.04s
2.0.2               0.55s      0.14s       0.04s
========= ========= ========== =========== =================

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


    times = []

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

            # print '%r (%r, %r) %2.2f sec' % (method.__name__, args, kw, te-ts)
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
        ssh.connect(host, username='root', password='', key_filename=os.path.expanduser('id_rsa') )

        # try:
        #     ssh.connect(host, username='root', password='', key_filename=os.path.expanduser('id_rsa') )
        # except paramiko.BadHostKeyException, paramiko.AuthenticationException:
        #     #_debug('_ssh_exec_paramiko','connection to %s with `id_rsa` ... FAILED' % host)
        #     try:
        #         ssh.connect(host, username='root', password='', key_filename=os.path.expanduser('~/.ssh/id_rsa') )
        #     except paramiko.BadHostKeyException, paramiko.AuthenticationException:
        #         #_debug('_ssh_exec_paramiko','connection to %s with `~/.ssh/id_rsa` ... FAILED' % host)
        #         raise SSH_AUTH_ERROR('Can not connect to host %s. You need to set a public key' % host)

    @timeit
    def ssh_commands(ssh, list_cmds):
        ### commands
        list_out = []
        for cmd in list_cmds:
            #_debug('_ssh_exec_paramiko','Try to execute "%s" ...' % cmd)
            stdin, stdout, stderr = ssh.exec_command(cmd)
            err = stderr.read()
            if err:
                #_debug('_ssh_exec_paramiko/exec cmd(%s)/sdterr' % cmd, err)
                raise SSH_EXEC_ERROR(err)
            else:
                #_debug('_ssh_exec_paramiko/exec cmd(%s)/sdterr' % cmd, 'OK')
                pass

            # rstripe \n on stdout
            for o in stdout.readlines():
                if o.endswith('\n'):
                    o = o[:-1]
                list_out.append(o)

        return list_out


    def print_long():
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

    for obj in times:
        print "%s: %.2f" % obj

    def print_short():
        def _p(t): 
            return "%.2fs" % t[1]

        print "paramiko(%s)" % paramiko.__version__,
        try:
            print "pycrypto(%s)" % Crypto.__version__,
        except:
            pass
        try:
            print "cryptography(%s)" % cryptography.__version__
        except:
            pass
        print
        print ' '.join(map(_p, times))


    # main 

    c = ssh_init()
    ssh_connect(c,'olympe')
    ssh_commands(c, ['uname'])
    c.close()

    #print_long()
    print_short()

