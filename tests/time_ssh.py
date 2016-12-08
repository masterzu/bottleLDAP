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

def ssh_commands(ssh, list_cmds):
    ### commands
    list_out = []
    
    @timeit
    def _ssh(cmd):
        return ssh.exec_command(cmd)

    for cmd in list_cmds:
        #_debug('_ssh_exec_paramiko','Try to execute "%s" ...' % cmd)
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
            #_debug('_ssh_exec_paramiko/exec cmd(%s)/sdterr' % cmd, err)
            out += '[err: %s]' % err
        else:
            #_debug('_ssh_exec_paramiko/exec cmd(%s)/sdterr' % cmd, 'OK')
            pass

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
