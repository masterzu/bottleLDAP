# -*- coding: utf-8 -*-
"""
bottleDAP - basic LDAP administration site using bottlepy Web Framework

To download latest 0.10 (stable) version 
(see https://github.com/masterzu/bottle/tags - my private depot)

# https://github.com/masterzu/bottle/blob/release-0.10/bottle.py


To launch the server just type:

# python server.py
"""

import os, os.path
import sys
import ConfigParser
import textwrap
import bottle
from bottle import route, run, view, template, static_file, request, redirect
from bottle import debug
import json
import ldap
import ldap.filter
import ldap.dn
import paramiko

__author__ = 'P. Cao Huu Thien'
__version__ = 9

"""
History
"""
main_news = ( 
    ('TODO', 'TODO', [
        "verification AJAX d'un login",
        "gestion des membres/directeurs",
        "gestion multi-NFS",
        "importation des utilisateurs depuis LDAP upmc.fr",
        "outils de gestion des utilsateurs: envoi d'email a tous les stagiaires/permanents/permanents ayant un stagiaires-doctorants ...",
        "outils de diagnostic: liste des utilisateurs sans email; stagiaires/phds sans directeur ...",
        "gestion de l'environnement POSIX sur le serveur NFS en SSH",
        ]),
    ('1', '1 Jan 1970',   [ u'(Très vieille) version initial :)' ]), 
    ('2', '12 Mars 2012', [ u'Passage à la version 0.10.9 de bottlepy' ]),
    ('3', '15 Mars 2012', [ 'Version alpha', 
        u'Première version fonctionnelle' ]),
    ('4', '27 Mars 2012', [ 'Fonctions de consultation disponibles', 
        'Ajout de la recherche avec JQuery']),
    ('5', '2 Avril 2012', [ 'Modification phase 1', 
        'Ajout des onglets (JQuery)', 
        u'Mise en place des requêtes AJAX (/api/)', 
        'interrogation et modification des champs modifiables de la fiche' ]),
    ('6', '11 Avril 2012', [ 'Modification phase 2', "ajout d'un compte permanent", 
        "suppression d'un compte" ]),
    ('7', '9 Mai 2012', [ 'Modification phase 3', "modification de champs directeur", 
        "ajout de jquery UI/autocomplete" ]),
    ('8', '10 Mai 2012', [ 'Modification phase 4', 
        u"ajout d'un compte doctorant/étudiant avec son directeur" ]),
    ('9', '21 Mai 2012', [ 'Modification phase 5', 
        u"création/suppression de l'environnement POSIX sur le serveur NFS en SSH", 
        u"HOME créé, Droits modifiés, Quotas appliqués"]
    ),
)




main_users = {
    '*': {
        'name': 'personnes',
        'basedn': 'ou=personnels,o=ijlrda',
    },
    'p': {
        'name': 'permanents',
        'basedn': 'ou=permanents,ou=personnels,o=ijlrda',
        'gid': 30000,
        'homebase': '/home/permanents/',
        'quotasoft': 0,
        'quotahard': 0,
    },
    'd': {
        'name': 'thésards',
        'basedn': 'ou=doctorants,ou=personnels,o=ijlrda',
        'gid': 40000,
        'homebase': '/home/doctorants/',
        'quotasoft': 0,
        'quotahard': 0,
    },
    't': {
        'name': 'étudiants et invités',
        'basedn': 'ou=temporaires,ou=personnels,o=ijlrda',
        'gid': 50000,
        'homebase': '/home/temporaires/',
        'quotasoft': 10485760,
        'quotahard': 20971520,
    },
}


main_nav = [ 
    ('/', 'accueil'), 
    ('*', 'serveurs'), 
    ('/server/olympe', 'master'), 
    ('/servers', 'liste'), 
    ('',''), 
    ('*', 'personnels'),
    ('_SEARCH_','rechercher...'),
    ('/users/p',main_users['p']['name']),
    ('/users/d',main_users['d']['name']),
    ('/users/t',main_users['t']['name']),
    ('',''), 
    ('*', 'structure'),
    ('/groups','équipes'),
    ('/users','utilisateurs'),
    ('','sites'),
    ('','réseaux'),
    ('',''), 
    ('*', 'site web'), 
    ('/news', 'news') , 
    ('/about', 'à propos')
    ]


main_ldap_server = {}

main_ldap_servers = []

main_ldap_servers_name = []

#----------------------------------------------------------
# Exceptions 
#----------------------------------------------------------

class ERROR(Exception):
    """
    base exception class for this project
    """
    def __init__(self, msg=None):
        if msg is None:
            self.msg=''
        else:
            self.msg = msg
    def __str__(self):
        return '[' + self.__class__ + '] ' + repr(self.msg)


class USER_TYPE_UNKNOWN(ERROR):
    pass

class USER_EXISTS(ERROR):
    """
    USER error
    """
    def __init__(self, user, msg=None):
        self.user = user
        ERROR.__init__(self,msg)


class USER_PERM_EXISTS(USER_EXISTS):
    """
    Use in _ldap_new_uid to usertype 'p'
    """
    def __init__(self):
        USER_EXISTS.__init__(self,user,msg='account "permanant" already exists !')

class USER_STAGIAIRE_LOGIN_FULL(USER_EXISTS):
    """
    Used in _ldap_new_uid to usertype 't'
    """
    pass

class POSIX(ERROR):
    pass

class POSIX_UID_FULL(POSIX):
    "Used in _ldap_new_posixAccount"
    pass

class SSH_ERROR(ERROR):
    def __init__(self):
        ERROR.__init__(self,'SSH error')
        
class SSH_AUTH_ERROR(SSH_ERROR):
    def __init__(self):
        ERROR.__init__(self,'SSH auth error')
    
class SSH_EXEC_ERROR(SSH_ERROR):
    def __init__(self, msg):
        ERROR.__init__(self, 'SSH exec error: '+msg)

#----------------------------------------------------------
# Privates Functions and Classes
#----------------------------------------------------------

class _colors:
    """
    Use with print to enable colors in console.
    """

    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    NONE = '\033[0m'

    def disable(self):
        self.HEADER = ''
        self.OKBLUE = ''
        self.OKGREEN = ''
        self.WARNING = ''
        self.FAIL = ''
        self.NONE = ''

def _debug(title, text=None):
    if not bottle.DEBUG:
        return
        
    if text is None:
        print _colors.HEADER + '[DEBUG] '+ _colors.OKGREEN + title + _colors.NONE
    else:
        if isinstance(text,type('qwe')):
            print _colors.HEADER + '[DEBUG] '+ _colors.OKGREEN + title + _colors.NONE + ' = ' + _colors.OKBLUE \
                + text + _colors.NONE
            #for t in textwrap.wrap(text, 80): print t
            #print text + _colors.NONE

        else:
            print _colors.HEADER + '[DEBUG] '+ _colors.OKGREEN + title + _colors.NONE + ' = ' + _colors.OKBLUE
            pprint(text)
            print _colors.NONE

def _debug_route():
    _debug("routing %s ..." % request.path)
    if len(request.params) > 0:
        _debug("    ... with %s" % repr(request.params.items()))

def _nav():
    """
    Calculate the current nav object depending on request.path 
    """
    nav = []
    for (l, n) in main_nav:
        if l == request.path:
           nav.append(('', n))
        else:
           nav.append((l, n))
    return nav

def _dict(**kargs):
    """
    Return the main dict used by routing functions
    """
    temp = dict(warn=None, nav=_nav(), author=__author__, version=__version__)
    temp.update(kargs.items())
    #_debug('_dict=', temp)
    return temp

def _json_result(**kargs):
    """
    Return json with mandatory field:
    * success
    """
    temp = dict(success=True)
    temp.update(kargs.items())
    _debug('_json_result=', temp)
    return temp

def _modules_version(mod):
    try:
        print _colors.HEADER + '[module] ' + _colors.OKBLUE + mod.__name__ + ' ' + _colors.OKGREEN + mod.__version__ + _colors.NONE
    except:
        pass

#----------------------------------------------------------
# HTML functions

def _html_escape(text):
    escape_table = {
        "&": "&amp;",
        '"': "&quot;",
        "'": "&apos;",
        ">": "&gt;",
        "<": "&lt;",
    }
    return "".join(escape_table.get(c,c) for c in text)

#----------------------------------------------------------
# private LDAP functions
# 
# Dont call none private function (ldap_initialize or else)
#+, It must be done in the caller function
#----------------------------------------------------------

def _ldap_uri(kargs):
    if 'host' not in kargs or 'name' not in kargs:
        return None
    if 'port' not in kargs:
        kargs['port'] = 389
    return "ldap://%s:%s" % (kargs['host'], kargs['port'])

def _ldap_initialize(kargs):
    """
    initialize the globale VAR main_ldap_server 

    return the filehandle of current LDAP server
        or None on error
    """
    global main_ldap_server

    if 'file' in main_ldap_server:
        _debug('LDAP', 'connexion to %s ... already connected.' % _ldap_uri(kargs))
        return main_ldap_server['file']

    try:
        l = ldap.initialize(_ldap_uri(kargs))
    except:
        _debug('LDAP', 'connexion to %s ... FAILED' % _ldap_uri(kargs))
        return None
    _debug('LDAP', 'connexion to %s ... DONE' % _ldap_uri(kargs))

    # construct the main connection object
    main_ldap_server = kargs
    main_ldap_server['file'] = l
    #_debug('main_ldap_server',main_ldap_server)
    return l

def _ldap_filter_base(list_filters):
    """
    convert list of <filter> to string (<f1>)(<f2>)...
    or <f> if singleton

    Dont use ldap.filter.filter_format HERE
    """
    filter = ''
    for f in list_filters:
        if not f: continue
        if f[0] == '(':
            filter += f
        else:
            filter += '('+f+')'
    #_debug('_ldap_build_ldapfilter_base/filter',filter)
    return filter


def _ldap_build_ldapfilter_and(list_filters):
    if list_filters is None:
        #_debug('_ldap_build_ldapfilter_and(None)')
        return ''
    if len(list_filters) == 0:
        #_debug('_ldap_build_ldapfilter_and([])')
        return ''
    if len(list_filters) == 1:
        resu = list_filters[0]
        #_debug('_ldap_build_ldapfilter_and([<singleton>]) = %s' % resu)
        return resu
    resu = '(&' + _ldap_filter_base(list_filters) + ')'
    #_debug('_ldap_build_ldapfilter_and', resu)
    return resu

def _ldap_build_ldapfilter_or(list_filters):
    if list_filters is None:
        #_debug('_ldap_build_ldapfilter_or(None)')
        return ''
    if len(list_filters) == 0:
        #_debug('_ldap_build_ldapfilter_or([])')
        return ''
    if len(list_filters) == 1:
        resu = list_filters[0]
        #_debug('_ldap_build_ldapfilter_or([<singleton>]) = %s' % resu)
        return resu
    resu = '(|' + _ldap_filter_base(list_filters) + ')'
    #_debug('_ldap_build_ldapfilter_or', resu)
    return resu

def _ldap_search(base, list_filters=[], list_attrs=None, filterstr=''):
    """
    general ldap search with base=base, scope=ldap.SCOPE_SUBTREE, filterstr=filters and attrlist=attrs

    Use filterstr instead of list_filters if not empty

    return ldap.search result
        or None if error

    May return Exception TIMEOUT if search time > 30s
    """

    if 'file' not in main_ldap_server or not main_ldap_server['file']:
        _debug('CALL _ldap_search', 'base=%s, list_filters=%s, list_attrs=%s, filterstr=%s - None (LDAP not connected?)' % (base, list_filters, list_attrs, filterstr))
        return None
    
    _debug('CALL _ldap_search', 'base=%s, list_filters=%s, list_attrs=%s, filterstr=%s' % (base, list_filters, list_attrs, filterstr))

    if filterstr:
        _filter = filterstr
    else:
        _filter = _ldap_build_ldapfilter_and(list_filters)

    objs = main_ldap_server['file'].search_st(base, ldap.SCOPE_SUBTREE, filterstr=_filter, attrlist=list_attrs, timeout=30)
    #_debug('RETURN _ldap_search',objs)
    return objs

def _ldap_modify_attr(dn, attr, val):
    """
    modify attribute for any entry:
    - not handle manager
    - cant change uid to ''
    - if val = '', use MOD_DELETE instead of MOD_REPLACE
    """
    if 'file' not in main_ldap_server:
        _debug('CALL _ldap_modify_attr','(dn=%s, attr=%s, val=%s) - No connexion to server' % (dn,attr,val))
        return None

    _debug('CALL _ldap_modify_attr','(dn=%s, attr=%s, val=%s)' % (dn,attr,val))

    
    # Dont handle manager because it is multi-valued
    if attr == 'manager':
        return None

    if attr == 'uid':
        # check for empty value
        if not val:
            return None

        # do the job
        objs = main_ldap_server['file'].modrdn_s(dn, list_modify_attrs)

    else:
        if val:
            list_modify_attrs = [(ldap.MOD_REPLACE, attr, [val])]
            _debug('_ldap_modify_attr/list_modify_attrs',list_modify_attrs)
        else:
            list_modify_attrs = [(ldap.MOD_DELETE, attr, None)]
            _debug('_ldap_modify_attr/list_modify_attrs',list_modify_attrs)

        # do the job
        objs = main_ldap_server['file'].modify_s(dn, list_modify_attrs)

    _debug('_ldap_modify_attr/modify_s',objs)
    return objs

def _ldap_delete_attr(dn, attr):
    return _ldap_modify_attr(dn, attr, '')
    
def _ldap_new_uid(givenName, sn, usertype):
    """
    Search and return a new uid (string)

    raise USER_EXISTS or USER_STAGIAIRE_LOGIN_FULL or USER_TYPE_UNKNOWN
    """
    _debug('CALL _ldap_new_uid','(givenName=%s, sn=%s, usertype=%s)' % (givenName, sn, usertype))

    if not givenName or not sn:
        return None

    if usertype == 'p' or usertype == 'd':
        gn = givenName[0].replace(' ','').lower()
        fn = sn.split()[0].replace(' ','').lower()
        uid = gn+fn
        _debug('_ldap_new_uid/uid',uid)

        ## FIXME check if newuid OK
        objs = _ldap_search(main_users[usertype]['basedn'], filterstr='uid=%s' % uid)
        if len(objs) != 0:
            _debug('_ldap_new_uid/uid','user %s alredy exists: exit' % uid)
            raise USER_EXISTS(uid)

        _debug('_ldap_new_uid/uid','login %s : OK' % uid)

        return uid

    elif usertype == 't':
        uid = None
        for i in range(1,200):
            objs = ldap_users(base=main_users[usertype]['basedn'], filterstr='uid=stagiaire%d' % i, list_attrs=['uid'])
            #_debug('_ldap_new_uid/for/objs',objs)
            if len(objs) == 0:
                uid = 'stagiaire%d' % i
                break
        if uid is None:
            raise USER_STAGIAIRE_LOGIN_FULL

        return uid

    # not suppose to be here
    raise USER_TYPE_UNKNOWN

def _ldap_new_posixAccount(usertype, uid):
    """
    Return uidNumber, gidNumber, homeDirectory (in string) 
    or None on error
    """
    _debug('CALL _ldap_new_posixAccount','(usertype=%s, uid=%s)' % (usertype,uid))

    if usertype not in ['p', 'd', 't']:
        raise USER_TYPE_UNKNOWN

    if not uid:
        return None

    gidNumber = main_users[usertype]['gid']
    homeDirectory = main_users[usertype]['homebase']+uid

    """
    if usertype == 'p':
        gidNumber = 30000
        homeDirectory = '/home/permanents/'+uid
    elif usertype == 'd':
        gidNumber = 40000
        homeDirectory = '/home/doctorants/'+uid
    else:
        gidNumber = 50000
        homeDirectory = '/home/temporaires/'+uid
    """
        
    objs = _ldap_search(main_users[usertype]['basedn'], filterstr='objectClass=person', list_attrs=['uidNumber'])
    #_debug('_ldap_new_posixAccount/objs',objs)
    _debug('_ldap_new_posixAccount/len(objs)',len(objs))

    _list_uidNumber = [o[1]['uidNumber'][0] for o in objs]
    _list_uidNumber.sort()
    #_debug('_ldap_new_posixAccount/_list_uidNumber',_list_uidNumber)
    

    uidNumber = gidNumber
    uidNumberMax = uidNumber + 10001

    for i in range(uidNumber,uidNumberMax):
        if repr(i) not in _list_uidNumber:
            _debug('_ldap_new_posixAccount/uidNumber','Found a free uidNumber: '+repr(i))
            break

    if i == (uidNumberMax - 1):
        raise POSIX_UID_FULL

    uidNumber = repr(i)
    gidNumber = repr(gidNumber)

    _debug('_ldap_new_posixAccount = ','(%s,%s,%s)' % (uidNumber, gidNumber, homeDirectory))
    return (uidNumber, gidNumber, homeDirectory)
        



def _ldap_useradd(dn, kargs):
    if 'file' not in main_ldap_server:
        _debug('CALL _ldap_useradd','(dn=%s, kargs=%s) - None (not connected?)' % (dn,kargs))
        return None

    _debug('CALL _ldap_useradd','(dn=%s, kargs=%s)' % (dn,kargs))

    # I dont use ldap.modlist because it may be buged !!
    list_modify_attrs=[]
    for k,v in kargs.items():
        list_modify_attrs.append((k,v))
    _debug('_ldap_useradd/list_modify_attrs',list_modify_attrs)

    # do the job
    objs = main_ldap_server['file'].add_s(dn, list_modify_attrs)

    return objs

def _json_user_getset_manager(uid, vals=None):
    """
    Get / Set special multivalued manager attr
    uid: uid of the user 
    vals: string with ; separated of managers' dn

    Return json obj
    """
    _debug('CALL _json_user_getset_manager','(%s, %s)' % (uid,vals))

    ldap_initialize(True)

    # get managers of user(uid)
    users = ldap_users(list_filters=['uid=%s' % uid], list_attrs=['manager'])
    _debug('_json_user_getset_manager/users',users)

    if vals is None:
        # mode GET
        _debug('_json_user_getset_manager/mode GET')

        if len(users) == 0:
            ldap_close()
            return _json_result(success=False, message='no user found')

        u = users[0][1]
        message = ''
        success=True

        try:
            vals = u['manager']
        except:
            vals = []
            message = 'manager not found'
            success = False
            ldap_close()
            return _json_result(success=success, message=message)

        # get (dn,cn) of all managers
        list_filters = []
        for dn in vals:
            list_filters.append(ldap.dn.explode_dn(dn)[0])

        users = ldap_users(base=main_users['p']['basedn'],filterstr=_ldap_build_ldapfilter_or(list_filters), list_attrs=['cn'])
        resu_dn = '; '.join([dn for dn, u in users]) + ' ; '
        resu_cn = ', '.join([u['cn'][0] for dn, u in users])
        _debug('_json_user_getset_manager/resu_dn',resu_dn)
        _debug('_json_user_getset_manager/resu_cn',resu_cn)

    else:
        # mode SET
        _debug('_json_user_getset_manager/mode SET')
       
        dn = users[0][0]
        try:
            old_managers_str = users[0][1]['manager']
        except:
            old_managers_str = ''
        _debug('_json_user_getset_manager/old_managers',old_managers_str)
        _vals = vals.rstrip('\s*;\s*')
        managers = _vals.split(';')
        _debug('_json_user_getset_manager/managers',managers)
        managers_len = len(managers)

        # check for managers existance
        # + and prepare the ldap/modify_s opp
        list_filters = []
        if old_managers_str != '':
            list_modify_attrs = [(ldap.MOD_DELETE, 'manager',None)]
        else:
            list_modify_attrs = []
        for _mandn in managers:
            mandn = _mandn.strip()
            if not mandn: continue

            try:
                _uid = ldap.dn.explode_dn(mandn, notypes=1)[0]     
            except ldap.DECODING_ERROR, e:
                resu = _json_result(success=False, message='invalid manager (dn=%s)' % mandn)
                resu['cn'] = old_managers_str
                return resu

            u = ldap_users(base=main_users['p']['basedn'], 
                filterstr='uid=%s' % _uid,
                list_attrs=['uid'])
            if len(u) != 1:
                return _json_result(success=False, message='invalid manager (uid=%s)' % _uid)
            else:
                _debug('_json_user_getset_manager/test manager',mandn+' OK')
            list_filters.append('uid=%s' % _uid)
            list_modify_attrs.append((ldap.MOD_ADD, 'manager', mandn))
        _debug('_json_user_getset_manager/list_modify_attrs',list_modify_attrs)

        # do the modify
        objs = main_ldap_server['file'].modify_s(dn, list_modify_attrs)

        if len(list_filters) > 0:
            # get the dn,cn of managers
            users = ldap_users(base=main_users['p']['basedn'],filterstr=_ldap_build_ldapfilter_or(list_filters), list_attrs=['cn'])
            resu_dn = '; '.join([dn for dn, u in users]) + ' ; '
            resu_cn = ', '.join([u['cn'][0] for dn, u in users])
        else:
            resu_dn = ''
            resu_cn = ''

        _debug('_json_user_getset_manager/resu_dn',resu_dn)
        _debug('_json_user_getset_manager/resu_cn',resu_cn)

                
    ldap_close()

    resu = _json_result()
    resu['dn'] = resu_dn
    resu['cn'] = resu_cn

    return resu

def _ssh_exec(host, user, list_cmds):
    """
    execute a list of ssh command - generic function

    Return a list of string (stdout and stderr) commands result
    or None on error
    """
    _debug('_ssh_exec(%s, %s, %s)' % (host, user, list_cmds))
    return _ssh_exec_paramiko(host, user, list_cmds)

def _ssh_exec_paramiko (host, user, list_cmds):
    """
    execute a list of command with paramiko - easy one

    Return a list of string (stdout and stderr) commands result
    
    Raise SSH_ERROR, SSH_AUTH_ERROR, SSH_EXEC_ERROR
    """
    try:
        from paramiko.util import hexlify
    except:
        _debug('_ssh_exec_paramiko','module paramiko.util not found. Return!')
        raise SSH_ERROR
        

    if not host or not user or len(list_cmds) == 0:
        return []

    paramiko.util.log_to_file('paramiko.log')

    ### client SSH
    ssh = paramiko.SSHClient()

    ### known_hosts
    ssh.load_system_host_keys()
    ssh.load_host_keys(os.path.expanduser('~/.ssh/known_hosts'))


    ### connection
    #ssh.connect(host, username='root', password='', pkey=private_key)
    try:
        ssh.connect(host, username='root', password='', key_filename=os.path.expanduser('~/.ssh/id_rsa') )
    except BadHostKeyException, AuthenticationException:
        raise SSH_AUTH_ERROR

    ### commands
    list_out = []
    for cmd in list_cmds:
        _debug('_ssh_exec_paramiko','Try to execute "%s" ...' % cmd)
        stdin, stdout, stderr = ssh.exec_command(cmd)
        err = stderr.read()
        if err:
            _debug('_ssh_exec_paramiko/exec cmd(%s)/sdterr' % cmd, err)
            raise SSH_EXEC_ERROR(err)
        else:
            _debug('_ssh_exec_paramiko/exec cmd(%s)' % cmd, 'OK')
        list_out = list_out + stdout.readlines()

    return list_out


def _ssh_exec_paramiko_extented(host, user, list_cmds):
    """
    execute a list of command with paramiko - step by step
    NOT USED

    Return a list of string of stdout and stderr commands result
    or None on error
    """
    import socket
    try:
        import paramiko
        from paramiko.util import hexlify
    except:
        _debug('_ssh_exec_paramiko_extented','module paramiko not found. Return!')
        return None

    paramiko.util.log_to_file('paramiko.log')

    ### 1. socket
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((host, 22))
    except Exception, e:
        _debug('_ssh_exec_paramiko_extented','*** Connect failed: ' + str(e))
        #traceback.print_exc()
        #sys.exit(1)
        return None

    ### 2. transport
    t = paramiko.Transport(sock)
    try:
        t.start_client()
    except paramiko.SSHException:
        _debug('_ssh_exec_paramiko_extented','*** SSH negotiation failed.')
        return None


    ### 3. check server's host key -- this is important.
    _debug('_ssh_exec_paramiko_extented','transport: '+repr(t))
    known_hosts = paramiko.util.load_host_keys(os.path.expanduser('~/.ssh/known_hosts'))
    host_key = t.get_remote_server_key()
    _debug('_ssh_exec_paramiko_extented/host_key',hexlify(host_key.get_fingerprint()))
    if host not in known_hosts or host_key.get_name() not in known_hosts[host]:
        _debug('_ssh_exec_paramiko_extented/host_key', 'Unknown host key!')
    elif known_hosts[host][host_key.get_name()] != host_key:
        _debug('_ssh_exec_paramiko_extented/host_key', '*** WARNING: Host key has changed!!! ')
        t.close()
        return None
    else:
        _debug('_ssh_exec_paramiko_extented/host_key', 'Host key OK.')


    ### 4. private keys
    #agent_auth(t, 'root')
    try:
        private_key = paramiko.RSAKey.from_private_key_file(os.path.expanduser('~/.ssh/id_rsa'))
    except paramiko.PasswordRequiredException:
        _debug('_ssh_exec_paramiko_extented','private key need password')
        private_key = paramiko.RSAKey.from_private_key_file(os.path.expanduser('~/.ssh/id_rsa'), '')

    _debug('_ssh_exec_paramiko_extented/private_key',hexlify(private_key.get_fingerprint()))
    _debug('_ssh_exec_paramiko_extented/private_key','Private key OK.')


    ### 5. auth_publickey
    try:
        t.auth_publickey(user, private_key)
    except paramiko.AuthenticationException, e:
        _debug( '*** Authentication failed. :(',e)
        t.close()
        return None

    ### 6. create a channel and execute in it
    list_out = []
    for cmd in list_cmds:
        chan = t.open_session()
        # do I need it ?
        #chan.get_pty()
        _debug('_ssh_exec_paramiko_extented/channel',repr(chan))
        _debug('_ssh_exec_paramiko_extented','Try to execute "%s" ...' % cmd)
        chan.exec_command(cmd)
        stdout = chan.makefile()
        chan.close()
        out = stdout.read()
        _debug('_ssh_exec_paramiko_extented/exec',cmd+'='+out)
        list_out.append(out)

    t.close()

    return list_out
    
def _ssh_exec_subprocess(host, user, list_cmds):
    """
    execute a list of command with ssh user@host

    Return a list of string (stdout and stderr) commands result
    FIXME: ssh user@host must have a empty key installed
    FIXME: does no work
    """
    import subprocess

    if not host or not user:
        return ''

    list_out = []
    for cmd in list_cmds:
        try:
            pout = subprocess.Popen( ['ssh','%s@%s' % (user, host), cmd],
                bufsize=1024, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, close_fds=True
                ).stdout
            out = pout.read() 
            pout.close()
        except subprocess.CalledProcessError:
            out = ''
            pass
        _debug('_ssh_exec_subprocess/'+cmd,out)
        list_out.append(out)
    return list_out
    
def _ssh_setquota(host,login,soft=0,hard=0):
    """
    Define a user quota on path as 'soft hard 0 0'

    return True if OK
    """
    if not host or not login:
        return False

    cmd = 'setquota -u ' + login + ' %d %d 0 0 /home' % (soft, hard) 
    _debug('_ssh_setquota(%s, %s, %d, %d)' % (host, login, soft, hard), 'cmd=%s' % cmd)

    try:
        _ssh_exec(host,'root', [cmd])
    except SSH_EXEC_ERROR:
        return False

    return True

#----------------------------------------------------------
# Public Functions
#----------------------------------------------------------

def ldap_load_config(filename):
    """
    Load the file and set the GLOBAL VAR main_ldap_servers
    """
    global main_ldap_servers, main_ldap_servers_name

    _debug('Loading configuration file "'+filename+'" ...')

    config = ConfigParser.RawConfigParser()
    config_attrs = {
        'name': '<server name>', 
        'host': '<server URL>', 
        'port': '<server port> OPTIONAL', 
        'basedn': '<base DN>', 
        'basegroup': '<DN of groupOfUniqueNames>', 
        'baseuser': '<DN of groupOfUniqueNames>', 
        'binddn': '<DN for bind()>', 
        'bindpwd': '<password for bind()>'}

    def usage():
        print
        print '#The syntax for the configuration file is:'
        print '[' + _colors.OKGREEN + '<server_id>' + _colors.NONE + ']'

        def t(name, text):
            print name + ' = ' + _colors.OKGREEN + text + _colors.NONE
    
        _keys_sorted = config_attrs.keys()
        _keys_sorted.sort()

        for k in _keys_sorted:
            t(k,config_attrs[k])

    config.read(filename)

    if not os.path.isfile(filename):
        print _colors.FAIL + 'Configuration File "%s" does not exists' % filename + _colors.NONE
        usage()
        sys.exit(1)

    sections = config.sections()
    if len(sections) == 0:
        print _colors.FAIL + 'no section in file \'%s\'' % os.path.abspath(filename) + _colors.NONE
        usage()
        sys.exit(1)
    
    for sec in sections:
        if not sec: continue
        _debug('loading section ['+sec+']')
        _dict = dict(config.items(sec))
        if 'port' not in _dict or not _dict['port']: _dict['port'] = 389
        main_ldap_servers.append(_dict)
        
    main_ldap_servers_name = [se['name'] for se in main_ldap_servers]
    #_debug('main_ldap_servers:',main_ldap_servers)

def ldap_initialize(bind=False):
    """
    initialize the LDAP server connection and put it to main_ldap_server

    return ldap object
        or False on error
    """
    h = _ldap_initialize(main_ldap_servers[0])
    if h is None: return False
    if bind:
        dn = main_ldap_server['binddn']
        pwd = main_ldap_server['bindpwd']
        _debug('ldap_initialize/binding',dn+':'+pwd)
        h.simple_bind_s(dn, pwd)
    return h
    

def ldap_close():
    global main_ldap_server

    if 'file' in main_ldap_server and main_ldap_server['file']:
        main_ldap_server['file'].unbind()

    del main_ldap_server['file']
    

def ldap_groups(list_filters=[], list_attrs=None):
    """
    return list of (dn, obj) of group with filters <list_filters>
        or [] on error
    """
    _debug('CALL ldap_groups', '(list_filters=%s, list_attrs=%s)' % (list_filters, list_attrs))

    if not ldap_initialize():
        return []

    base = main_ldap_server['basegroup']

    # filter build
    if 'objectClass=groupOfUniqueNames' not in list_filters:
        list_filters.append('objectClass=groupOfUniqueNames')

    _debug('ldap_groups/list_filters',list_filters)

    return _ldap_search(base, list_filters=list_filters, list_attrs=list_attrs)
    
   
def ldap_users(base=None, list_filters=None, list_attrs=None, filterstr=''):
    """
    return list of (dn, obj) of users with filters <list_filters>
        or [] on error
    """
    _debug('CALL ldap_users', "(base=%s\n, list_filters=%s\n, list_attrs=%s\n, filterstr=%s)" 
        % (base, list_filters, list_attrs, filterstr))


    if not ldap_initialize():
        return []

    if base is None:
        base = main_ldap_server['baseuser']

    if list_filters is None:
        list_filters = []


    # HACK to avoid uid=test
    nontest = '(!(uid=test))'
    if nontest not in list_filters:
        list_filters.append(nontest)

    # add object person
    if 'objectClass=person' not in list_filters:
        list_filters.append('objectClass=person')

    # add filterstr
    if filterstr not in list_filters:
        list_filters.append(filterstr)

    _debug('ldap_users/list_filters',list_filters)

    objs = _ldap_search(base, list_filters, list_attrs)
    _debug('ldap_users/objs',objs)

    return objs
    
def ldap_users_by_type(type):
    """
    return list of (dn, obj) from users with type <type>
        or []
    """
    _debug('CALL ldap_users_by_type', '(%s)' % type)
    if type not in ('p', 'd', 't', '*'):
        _debug('ldap_users_by_type/type', 'type "%s" unknown' % type)
        return []

    base = main_users[type]['basedn']
    return ldap_users(base=base, list_attrs=['uid','cn','sn','givenName','mail'])

#----------------------------------------------------------
# Routing Functions

@route('/static/<filepath:path>')
def static(filepath):
    return static_file(filepath, root=os.path.join('.', 'static'))


@route('/')
@view('index')
def index():
    _debug_route()
    return _dict(news=main_news)

@route('/servers')
@view('servers')
def servers():
    _debug_route()
    return _dict(servers=main_ldap_servers_name)

@route('/server/<server>')
def server_attr(server=None):
    """print server information
    use mulpiple template : 
    * server_att : for good request
    * servers : for warning redirection
    """
    _debug_route()
    for se in main_ldap_servers:
        if 'name' not in se:
            _debug('server_attr/se[name]','Dont exists !!')
            continue
        if se['name'] == server:
            ldap_kargs = se
            ldap_conn = _ldap_initialize(ldap_kargs)
            if ldap_conn is None:
                return template('servers', _dict(warn='LDAP server "%s" connexion error' 
                    % server, servers=main_ldap_servers_name))
            return template('server_attr', _dict(name=se['name'], server=se))

    return template('servers', _dict(warn='LDAP server "%s" not found' % server, servers=main_ldap_servers_name))


@route('/groups')
@view('groups')
def groups():
    _debug_route()
    ldap_initialize()
    groups = ldap_groups(list_attrs=['cn','description'])
    ldap_close()
    if groups is None:
        return _dict(warn='LDAP main server "%s" error' % main_ldap_server['name'], groups={})
    return _dict(groups=groups)

@route('/group/<group>')
@view('group')
def group(group=None):
    _debug_route()
    if group is None:
        return _dict(warn='ERROR: route group(None)', cn='', desc='', members=[])
    ldap_initialize()
    grs = ldap_groups(list_filters=['cn=%s' % group], list_attrs=['cn','description','uniqueMember'])
    _debug('groups/grs',grs)
    if len(grs) == 0:
        ldap_close()
        return _dict(warn='Le groupe "%s" n\'existe pas' % group, cn='Inexistant', desc='', members=[])
    if len(grs) != 1:
        ldap_close()
        return _dict(warn='ERROR: ldap_groups(None,[cn=%s])' % group, cn='Inexistant', desc='', members=[])
    (dn,obj) = grs[0]
    if 'description' in obj:
        desc = obj['description'][0]
    else:
        desc = ''

    list_filters=[]
    for user_dn in obj['uniqueMember']:
        user_uid = ldap.dn.explode_dn(user_dn)[0]
        list_filters.append(user_uid)
    _filter = _ldap_build_ldapfilter_or(list_filters)
    _members = _ldap_search(main_ldap_server['baseuser'], filterstr=_filter, list_attrs=['cn', 'uid'])
    members = [ {'uid': o['uid'][0], 'cn': o['cn'][0]} for d,o in _members ]
    ldap_close()
    return _dict(cn=obj['cn'][0], desc=desc, members=members)


@route('/users/search/<str_filter>')
@view('users_search')
def users_search(str_filter):
    """
    return list of users with string filter=<str_filter>
    """
    _debug_route()
    #_debug('users_search/str_filter',str_filter)
    _filter = ldap.filter.escape_filter_chars(str_filter)
    #_debug('users_search/_filter',_filter)

    _list_filters = []
    for st in ['cn', 'sn', 'givenName','uid']:
        _list_filters.append('%s=*%s*' % (st, _filter))
        _list_filters.append('%s~=%s' % (st, _filter))
        
    _filters = _ldap_build_ldapfilter_or(_list_filters)

    ldap_initialize()
    try:
        users = ldap_users(filterstr=_filters)
    except ldap.TIMEOUT:
        ldap_close()
        return _dict(warn=u"Réponse du serveur trop longue pour la recherche %s" % str_filter, 
            users=[], query=str_filter, ldap_filter=_filters)

    if len(users) == 0:
        ldap_close()
        return _dict(warn="Pas d'utilisateur trouvé pour %s" % str_filter, 
            users=[], query=str_filter, ldap_filter=_filters)
        
    ldap_close()
    return _dict(users=users, query=str_filter, ldap_filter=_filters)

@route('/users')
@route('/users/<type>')
@view('users_type')
def users_type(type=None):
    _debug_route()
    
    if type is None:
        type = '*'

    if type not in main_users.keys():
        redirect('/users/*')

    title = main_users[type]['name']
    ldap_initialize()
    try:
        users = ldap_users_by_type(type)
    except ldap.TIMEOUT:
        ldap_close()
        return _dict(warn='LDAP server too long. Retry later :(', title=title, users=[])

    if len(users) == 0:
        ldap_close()
        return _dict(warn='No users of type %s' % title, title=title, users=[])
        
    ldap_close()
    return _dict(title=title, users=users)


@route('/user/<uid>')
@view('user')
def user(uid):
    _debug_route()

    # special uid * for the search form
    #if uid == '*':
    #    return _dict(users=[], uid=uid)
    
    # connect as root to access userPassword
    ldap_initialize(True)
    users = ldap_users(list_filters=['uid=%s' % uid])
    if len(users) == 0:
        ldap_close()
        return _dict(warn='Pas d\'utilisateurs trouvé pour uid=%s' % uid, users=[], uid=uid)
    if len(users) > 1:
        warn=u'Plusieurs utilisateur ont le même uid'
    else:
        warn=None

    # manager
    # FIXME handle only one manager per user for the first user
    managers = []
    d, u = users[0]
    if 'manager' in u:
        for mandn in u['manager']:
            manuid = ldap.dn.explode_dn(mandn, notypes=1)[0]
            man = ldap_users(base=main_users['p']['basedn'], list_filters=['uid=%s' % manuid], list_attrs=['cn', 'uid'])
            if len(man) > 0:
                managers.append(man[0])

    # external fields

    # PHDs
    # FIXME: handle only the first user
    phds = []
    d, u = users[0]
    studs = ldap_users(base=main_users['d']['basedn'], list_filters=['manager=%s' % d], list_attrs=['cn', 'uid', 'description'])
    for studn, stu in studs:
        _debug('user/phd',stu)
        phds.append(stu)

    # students
    # FIXME: handle only the first user
    students = []
    d, u = users[0]
    studs = ldap_users(base=main_users['t']['basedn'], list_filters=['manager=%s' % d], list_attrs=['cn', 'uid', 'description'])
    for studn, stu in studs:
        _debug('user/stu',stu)
        students.append(stu)

    # equipe
    # FIXME: handle only the first user
    # FIXME:         and the first team
    d, u = users[0]
    teams = _ldap_search(base='ou=equipes,o=ijlrda', filterstr='(&(objectClass=groupOfUniqueNames)(uniqueMember=%s))' % d, list_attrs=['cn','description'])
    _debug('user/teams',teams)

    ldap_close()
    return _dict(warn=warn, users=users, uid=uid, managers=managers, students=students, phds=phds, teams=teams)

@route('/news')
@route('/news/<ver>')
@view('news')
def news(ver=None):
    _debug_route()
    return _dict(ver=ver, news=main_news)



@route('/about')
@view('about')
def about():
    _debug_route()
    return _dict(warn=None, ldap_ver=ldap.__version__, bottle_ver=bottle.__version__)

#----------------------------------------------------------
# Routing JSON Functions

@route('/api/useradd', method='POST')
def json_useradd():
    """
    add user and return the uid of the new user
    or None on error

    Mandatory fields passed in POST: 
    'cn', 'sn', 'givenName', 'mail', 'description', 'usertype'
    
    Mandatory fields for usertype == p:
    'group'

    Mandatory fields for usertype == t or d:
    'manager'

    Optional fields:
    'uid'

    """
    _debug_route()
    datas = request.params
    ldap_data = {}

    ### LDAP operations

    # mandatory/LDAP attrs
    for attr in ['cn', 'sn', 'givenName', 'mail', 'description']:
        if attr not in datas or not datas[attr]:
            return _json_result(success=False, message='missing mandatory/LDAP parameter: '+attr)
        ldap_data[attr] = [datas[attr]]
        # add local variable: `attr` = datas[attr]
        

    # mandatory/none LDAP attrs
    for attr in ['usertype']:
        if attr not in datas or not datas[attr]:
            return _json_result(success=False, message='missing mandatory/none LDAP parameter: '+attr)
        usertype = datas['usertype']

    if usertype not in ['p', 'd', 't']:
        return _json_result(success=False, message='bad attr usertype: '+usertype)
    
    # usertype == p mandatory attrs
    if usertype == 'p':
        for attr in ['group']:
            if attr not in datas or not datas[attr]:
                return _json_result(success=False, message='missing permanents parameter: '+attr)
    # usertype == t|d mandatory attrs
    elif usertype == 'd' or usertype == 't':
        if 'manager' not in datas or not datas['manager']:
            return _json_result(success=False, message='missing PHD/student parameter: '+'manager')

    ldap_initialize(True)
    if 'uid' in datas and datas['uid']:
        uid = datas['uid']
    else:
        try:
            uid = _ldap_new_uid(datas['givenName'], datas['sn'], datas['usertype'])
        except USER_EXISTS:
            ldap_close()
            return _json_result(success=False, message='user_exists')
        except USER_STAGIAIRE_LOGIN_FULL:
            ldap_close()
            return _json_result(success=False, message='no_emtpy_uid')
    _debug('json_useradd/uid',uid)
            

    try:
        _t = _ldap_new_posixAccount(usertype, uid)
    except POSIX_UID_FULL:
        ldap_close()
        return _json_result(success=False, message='pas de d information POSIX disponible pour %s' % uid)

    uidNumber, gidNumber, homeDirectory = _t

    def passwd(size=8):
        import string
        from random import choice
        _list = (string.letters + string.digits).translate(None,'1lo0')
        return ''.join([choice(_list) for i in range(size)])

    userPassword = passwd()

    dn = 'uid=' + uid + ',' + main_users[datas['usertype']]['basedn'] 
    _debug('dn='+dn)

    ldap_data['objectClass'] = ['top', 'person', 'organizationalPerson', 'inetOrgPerson', 'posixAccount']
    ldap_data['homeDirectory'] = [homeDirectory]
    ldap_data['loginShell'] = ['/bin/bash']
    ldap_data['uid'] = [uid]
    ldap_data['userPassword'] = [userPassword]
    ldap_data['uidNumber'] = [uidNumber]
    ldap_data['gidNumber'] = [gidNumber]
    if usertype == 'd' or usertype == 't':
        _attr = datas['manager'].rstrip('\s*;\s*')
        ldap_data['manager'] = []
        for man in _attr.split(';'):
            _man = man.strip()
            if _man:
                ldap_data['manager'].append(_man)
    _debug('ldap_data',ldap_data)

    # user creation
    try:
        objs = _ldap_useradd(dn, ldap_data)
    except ldap.LDAPError, e:
        _debug('json_useradd/Exception',repr(e))
        return _json_result(success=False, message='message du serveur LDAP: '+repr(e))

    # group update
    if usertype == 'p':
        group = datas['group']
        list_modify_attrs = [(ldap.MOD_ADD, 'uniqueMember', dn)]
        #_debug('json_useradd/list_modify_attrs',list_modify_attrs)
        try:
            objs = main_ldap_server['file'].modify_s(group, list_modify_attrs)
        except ldap.LDAPError,e:
            return _json_result(success=False, message='message du serveur LDAP: '+repr(e))
            
    ldap_close()

    ### NFS operations
    list_print_cmds = []
    for text, cmd in [
        ('creation du HOME par copie des fichiers /etc/skel','cp -r /etc/skel %s' % homeDirectory),
        (u'changement du propriétaire','chown -R %s:%s %s' % (uidNumber, gidNumber, homeDirectory)),
        ('changement des droits','chmod -R u=rwx,go= %s' % homeDirectory),
        ]:
        _debug('json_useradd/Try to exec %s [%s]' % (cmd, text))
        try:
            _ssh_exec(main_ldap_server['host'],'root',[cmd])
        except SSH_EXEC_ERROR as e:
            return _json_result(success=False, message=e.msg)
        _debug('json_useradd/Try to exec %s' % cmd, 'OK')

    
    if not _ssh_setquota(main_ldap_server['host'], 
            uid, 
            main_users[usertype]['quotasoft'], 
            main_users[usertype]['quotahard']) :
        return _json_result(success=False, message='erreur de Quota')

            
    return _json_result(success=True, uid=uid, userPassword=userPassword, message=u'répertoire crée, droits changés, quotas appliqués')

@route('/api/userdel', method='POST')
def json_userdel():
    _debug_route()
    datas = request.params
    if 'uid' not in datas or not datas['uid']:
        return _json_result(success=False, message='missing parameter: uid')

    uid = datas['uid']

    ldap_initialize(True)

    objs = _ldap_search(main_users['*']['basedn'], list_filters=['objectClass=person','uid='+uid])
    if len(objs) != 1:
        return _json_result(success=False, message="pas d'utilisateur %s" % uid)

    dn = objs[0][0]
    _debug('json_userdel/dn',dn)
    homeDirectory = objs[0][1]['homeDirectory'][0]
    _debug('json_userdel/homeDirectory',homeDirectory)

    groups = _ldap_search(main_ldap_server['basegroup'], 
        list_filters=['objectClass=groupOfUniqueNames','uniqueMember=%s' % dn], 
        list_attrs=['cn'])

    if len(groups) != 0:
        list_modify_attrs = [(ldap.MOD_DELETE, 'uniqueMember', dn)]
        for dngroup, group in groups:
            cn = group['cn'][0]
            _debug('json_userdel/group', 'removing %s from %s ...' % (uid, cn))
            try: 
                main_ldap_server['file'].modify_s(dngroup, list_modify_attrs)
            except ldap.LDAPError,e:
                return _json_result(success=False, message="serveur LDAP message: %s" % str(e))
            _debug('json_userdel/group', 'removing %s from %s ... OK' % (uid, cn))
    else:
        _debug('json_userdel','no group with member '+dn)
            

    _debug('json_userdel/user','deleting user %s ...' % uid)
    try:
        main_ldap_server['file'].delete_s(dn)
    except ldap.LDAPError, e:
        return _json_result(success=False, message='message du serveur LDAP: '+repr(e))
    _debug('json_userdel/user','deleting user %s ... OK' % uid)
        
    ldap_close()

    ### NFS operations
    _ssh_exec(main_ldap_server['host'],'root',['rm -rf ' + homeDirectory])
    

    return _json_result(success=True)

@route('/api/user/<uid>/attr/<attr>', method='POST')
def json_user_set_attr(uid,attr):
    """
    Set user attr with POST method
    """
    _debug_route()
    datas = request.params
    _debug('json_user_set_attr/datas.keys',datas.keys())
    if not attr:
        return _json_result(success=False, message='no parameters attr')

    try:
        newval = datas['newval']
    except:
        return _json_result(success=False, message='wrong parameters')

    # handle multi-valuation manager
    if attr == 'manager':
        return _json_user_getset_manager(uid, newval)

    ldap_initialize(True)

    users = ldap_users(list_filters=['uid=%s' % uid], list_attrs=[attr])
    _debug('json_user_set_attr/users',users)

    if len(users) == 0:
        ldap_close()
        return _json_result(success=False, message='wrong parameters; Users %s do not exists' % uid)

    dn = users[0][0]

    try:
        if _ldap_modify_attr(dn, attr, newval) is None:
            raise ldap.LDAPError, "can't change attribut %s" % attr 
    except ldap.LDAPError, e:
        ldap_close()
        return _json_result(success=False, message='LDAP ERROR (%s)' % e)
        
    resu =_json_result(success=True)
    resu[attr] = newval
    _debug('json_user_set_attr=',resu)

    ldap_close()
    return resu



@route('/api/user/<uid>/attr/<attr>')
def json_user_get_attr(uid,attr):
    """
    Get user attr
    """
    _debug_route()

    if not uid or not attr:
        return _json_result(success=False, message='bad parameters')

    if attr == 'manager':
        return _json_user_getset_manager(uid)
    
    if attr == 'userPassword':
        ## FIXME must be protected by some auth mecanism
        ldap_initialize(True)
    else:
        ldap_initialize()

    users = ldap_users(list_filters=['uid=%s' % uid], list_attrs=[attr])
    _debug('json_user_get_attr/users',users)

    ldap_close()

    if len(users) == 0:
        return _json_result(success=False, message='no user found')

    u = users[0][1]
    message = ''
    success=True
    try:
        # take only the first value
        val = u[attr][0]
    except:
        val = ''
        message = attr + ' not found'
        success=False
    #_debug('json_user_get_attr/val',val)
    resu = _json_result(success=success, message=message)
    resu[attr]=val
    _debug('json_user_get_attr/resu',resu)
    return resu


@route('/api/groups')
def json_groups():
    """
    Get group lists
    """
    _debug_route()

    ldap_initialize()
    groups = ldap_groups(list_attrs=['cn','description'])
    ldap_close()

    if groups is None:
        return _json_result(success=False, message='no group found')

    _list = []
    for dn,g in groups:
        _d = {'cn': g['cn'][0], 'description': g['description'][0], 'dn': dn}
        _list.append(_d)

    resu = _json_result()
    resu['groups'] = _list

    return resu

@route('/api/autocomplete_manager')
def json_autocomplete_manager():
    """
    search for permanents user with 
    term=<search string>
    """
    _debug_route()
    datas = request.params
    try:
        term = datas['term']
    except:
        return ['no term']
        #return _json_result(success=False, message='wrong parameters')

    if term == '':
        return ['term empty']

    _term = ldap.filter.escape_filter_chars(term)

    _list_filters = []
    for st in ['cn', 'sn', 'givenName','uid']:
        _list_filters.append('%s=*%s*' % (st, _term))
        _list_filters.append('%s~=%s' % (st, _term))
        
    _filters = _ldap_build_ldapfilter_or(_list_filters)

    ldap_initialize()
    json_resu = []
    try:
        users = ldap_users(base=main_users['p']['basedn'], filterstr=_filters)
    except ldap.TIMEOUT:
        users = []
        pass
        #return _json_result(succes=False, message=u"Réponse du serveur trop longue pour la recherche %s" % term)
    ldap_close()

    # return only the first 10 items
    _users = users[0:10]
    _debug('json_autocomplete_manager/users', users)

    for dn,o in _users:
        resu = dict(id=dn, label=o['cn'][0], value=dn)
        _debug('json_autocomplete_manager/resu',resu)
        json_resu.append(resu)
   
    _debug('json_autocomplete_manager/json_resu',json_resu)
    return json.dumps(json_resu)


@route('/api/server/<server>')
def json_server(server):
    """
    check for local info in server with ssh
    """
    _debug_route()

    if not server: 
        return _json_result(success=False, message='Server not specified')

    host = ''
    for se in main_ldap_servers:
        if 'name' in se and se['name'] == server:
            host = se['host']
            break

    if not host:
        return _json_result(success=False, message='Server %s unknown' % server)
  
    try: 
        output = _ssh_exec(host,'root',['hostname'])
    except SSH_EXEC_ERROR as e:
        return _json_result(success=False, message=e.msg)

    if output is None:
        resu = _json_result(success=False, message="SSH auth failed")
    else:
        resu = _json_result(message="\n".join(output))
    _debug('json_server/resu',resu)

    return resu
    

#----------------------------------------------------------
# MAIN

if __name__ == '__main__':

    #----------------------------------------------------------
    # DEBUG MODE
    #----------------------------------------------------------

    debug(True)
    for m in [ConfigParser, textwrap, bottle, json, ldap, paramiko]:
        _modules_version(m)

    import pprint
    pprint = pprint.PrettyPrinter(indent=4).pprint
    print _colors.OKBLUE + 'mode DEBUG' + _colors.NONE
    ldap_load_config('ldap_servers.ini')
    run(host='0.0.0.0', port=8080, reloader=True)
    

    #----------------------------------------------------------
    # PROD MODE
    #----------------------------------------------------------
    #pprint = __buidin__.print
    #ldap_load_config('ldap_servers.ini')
    #run(host='0.0.0.0', port=80)

 

# vim:spelllang=en:
