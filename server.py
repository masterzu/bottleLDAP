# -*- coding: utf-8 -*-
"""
bottleDAP - basic LDAP administration site using bottlepy Web Framework

To download latest 0.10 (stable) version 
(see https://github.com/masterzu/bottle/tags - my private depot)

# https://github.com/masterzu/bottle/blob/release-0.10/bottle.py


To launch the server just type:

# python server.py

### code checked with Google Python Style Guide
### http://google-styleguide.googlecode.com/svn/trunk/pyguide.html
"""

### standard libraries
import os, os.path
import sys
import json
import ConfigParser
import pprint
import textwrap

### external libraries
import bottle
import ldap
import ldap.filter
import ldap.dn
import paramiko

__author__ = 'P. Cao Huu Thien'
__version__ = 'devel'

"""
History
"""
main_news = ( 
    ('TODO', 'TODO', [
    'FIXME: json_userdel(): check if user have students',
    'FIXME: supprimer les lettres lI du generateur de mot de pass',
        "verification AJAX d'un login",
        "gestion des membres/directeurs",
        "gestion multi-NFS",
        "importation des utilisateurs depuis LDAP upmc.fr",
        "outils de gestion des utilsateurs: envoi d'email a tous les stagiaires/permanents/permanents ayant un stagiaires-doctorants ...",
        "outils de diagnostic: liste des utilisateurs sans email; stagiaires/phds sans directeur ...",
        ]),
    ('1', '1 Jan 1970',   [ u'(Très vieille) version initiale :)' ]), 
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
    ('10', '12 Sept 2012', [ 'Modification sur demande', 
        u"changement de login pour les étudiants : suppression du motif <stagiaireX>",
        u"BUGFIX: vérification du login unique lors de la création un compte"]
    ),
    ('11', '22 Oct 2012', [ 'Modification phase 6', 
        'passage a bottle 0.11.x', 
        'gestion multi-serveur NFS/LDAP (ldap_servers.ini, nfs_servers.ini)',
        'tableau de bord des serveurs LDAP/NFS (graphes des quotas pour serveurs NFS, version des distrib et noyau linux)',
        'DEVEL: utilisation du Google Python Style Guide avec pychecker',
        ]
    ),
    ('devel', 'Nov 2012', [ 'Modification phase 7', 
        "integration de l'overlay ppolicy"
        'test matisse',
        'création des logs, stoqués dans mongoDB'
        ]
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
        'homebase': '/%s/permanents/',
        'quotasoft': 0,
        'quotahard': 0,
    },
    'd': {
        'name': u'thésards',

        'basedn': 'ou=doctorants,ou=personnels,o=ijlrda',
        'gid': 40000,
        'homebase': '/%s/doctorants/',
        'quotasoft': 0,
        'quotahard': 0,
    },
    't': {
        'name': u'étudiants et invités',
        'basedn': 'ou=temporaires,ou=personnels,o=ijlrda',
        'gid': 50000,
        'homebase': '/%s/temporaires/',
        'quotasoft': 10485760,
        'quotahard': 20971520,
    },
}

main_ldap_server = {}

main_ldap_servers = []
main_ldap_servers_name = []

main_nfs_servers = []
main_nfs_servers_name = []

main_admins = []

# mongoDB database
#+ fields:
#+  hostname (default localhosr)
#+  port (default 27017)
#+  db (default bottleldap)
mongodb = {
    'hostname': 'localhost',
    'port': 27017,
    'db': 'bottleldap'
}



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
    def __init__(self, msg=None):
        if (msg is None):
            ERROR.__init__(self,'SSH error')
        else:
            ERROR.__init__(self,'SSH error: '+msg)
        
class SSH_AUTH_ERROR(SSH_ERROR):
    def __init__(self, msg='SSH AUTH error'):
        ERROR.__init__(self, msg)
    
class SSH_EXEC_ERROR(SSH_ERROR):
    def __init__(self, msg='SSH EXEC error'):
        ERROR.__init__(self, msg)

class EXEC_NOSERVER(ERROR):
    def __init__(self, msg):
        ERROR.__init__(self, 'EXEC on unknown server: '+msg)

class EXEC_NOTALLOW(ERROR):
    def __init__(self, msg):
        ERROR.__init__(self, 'EXEC not allow: '+msg)

class MONGODB_ERROR(ERROR):
    pass


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
    NOCOLOR = '\033[0m'

    def disable(self):
        self.HEADER = ''
        self.OKBLUE = ''
        self.OKGREEN = ''
        self.WARNING = ''
        self.FAIL = ''
        self.NOCOLOR = ''

def _debug(title, text=None):
    if not bottle.DEBUG:
        return
    pp = pprint.PrettyPrinter(indent=7).pprint

    _tab = _colors.HEADER + "      | "
        
    if text is None:
        print _colors.HEADER + '[DEBUG] '+ _colors.OKGREEN + title + _colors.NOCOLOR
    else:
        if isinstance(text,type('qwe')):
            print _colors.HEADER + '[DEBUG] '+ _colors.OKGREEN + title + _colors.NOCOLOR + ' : '
            for t in textwrap.wrap(text, 80): 
                print _tab + _colors.OKBLUE + t


        else:
            print _colors.HEADER + '[DEBUG] '+ _colors.OKGREEN + title + _colors.NOCOLOR + ' = ' + _colors.OKBLUE
            pp(text)
            print _colors.NOCOLOR

def _debug_route():
    _debug("routing %s ..." % bottle.request.path)
    if len(bottle.request.params) > 0:
        _debug("    ... with %s" % repr(bottle.request.params.items()))

def _nav():
    """
    Calculate the current nav object depending on request.path 
    """
    nav = []
    for (l, n) in main_nav:
        if l == bottle.request.path:
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
        print _colors.HEADER + '[module] ' + _colors.OKBLUE + mod.__name__ + ' ' + _colors.OKGREEN + mod.__version__ + _colors.NOCOLOR
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
    _filter = ''
    for f in list_filters:
        if not f: continue
        if f[0] == '(':
            _filter += f
        else:
            _filter += '('+f+')'
    #_debug('_ldap_build_ldapfilter_base/filter',_filter)
    return _filter


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
    

    if filterstr:
        _filter = filterstr
    else:
        _filter = _ldap_build_ldapfilter_and(list_filters)
    _debug('_ldap_search/_filter', _filter)

    _debug('CALL _ldap_search', 'base=%s, list_filters=%s, list_attrs=%s, filterstr=%s' % (base, list_filters, list_attrs, filterstr))
    objs = main_ldap_server['file'].search_st(base, ldap.SCOPE_SUBTREE, filterstr=_filter, attrlist=list_attrs, timeout=30)
    #_debug('RETURN _ldap_search',objs)
    return objs

def _ldap_modify_attr(dn, attr, val):
    """
    modify attribute for any entry:
    - not handle manager
    - cant change uid to ''
    - if val = '', use MOD_DELETE instead of MOD_REPLACE

    Return None on error
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
        # FIXME objs = main_ldap_server['file'].modrdn_s(dn, list_modify_attrs)
        return None

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

    if usertype == 'p' or usertype == 'd' or usertype == 't':
        gn = givenName[0].replace(' ','').lower()
        fn = sn.split()[0].replace(' ','').lower()
        uid = gn+fn
        _debug('_ldap_new_uid/uid',uid)

        ## FIXME check if newuid OK
        objs = _ldap_search(main_users['*']['basedn'], filterstr='uid=%s' % uid)
        if len(objs) != 0:
            _debug('_ldap_new_uid/uid','user %s alredy exists: exit' % uid)

            # check uid+number from 1 to 99
            for i in range(1,100):
                uidn = '%s%i' % (uid,i)
                objs = _ldap_search(main_users['*']['basedn'], filterstr='uid=%s' % uidn)
                if len(objs) != 0:
                    _debug('_ldap_new_uid/uid','user %s alredy exists: exit' % uidn)
                else:
                    _debug('_ldap_new_uid/uid','login %s : OK' % uidn)
                    return uidn
                    
            raise USER_EXISTS(uid)

        _debug('_ldap_new_uid/uid','login %s : OK' % uid)

        return uid

    #elif usertype == 't':
    #    uid = None
    #    for i in range(1,200):
    #        objs = ldap_users(base=main_users[usertype]['basedn'], filterstr='uid=stagiaire%d' % i, list_attrs=['uid'])
    #        #_debug('_ldap_new_uid/for/objs',objs)
    #        if len(objs) == 0:
    #            uid = 'stagiaire%d' % i
    #            break
    #    if uid is None:
    #        raise USER_STAGIAIRE_LOGIN_FULL
    #    return uid

    # not suppose to be here
    raise USER_TYPE_UNKNOWN

def _ldap_new_posixAccount(usertype, uid, hostname):
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

    # FIXME : Dirty Hack for olympe : homeDirectory = /home/{group}/{user}
    
    if hostname=='olympe':
        homeDirectory = (main_users[usertype]['homebase'] % 'home')+uid
    else:
        homeDirectory = (main_users[usertype]['homebase'] % hostname)+uid

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
            except ldap.DECODING_ERROR:
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
        main_ldap_server['file'].modify_s(dn, list_modify_attrs)

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

def json_exec_common(server, cmd):
    """
    Common command executed to all NFS and LDAP servers.

    Args:
        server: the server name in main_ldap_servers or main_nfs_servers
        cmd: command ID for a list of command to execute on server

    Returns:
        dict like in _json_result used by bottle template
    """

    ssh_kcmds = {
        'issue': ['cat /etc/issue | head -1'],
        'uname': ['uname -a']
    }

    host = ''
    user = 'root'

    _list = main_ldap_servers + main_nfs_servers
    for se in _list:
        if 'name' in se and se['name'] == server:
            host = se['host']
            break

    if not host or not server:
        return _json_result(success=False, message='serveur %s inconnu' % server)

    if cmd not in ssh_kcmds:
        return _json_result(success=False, message='command interdite')

    try: 
        output = _ssh_exec(host, user, ssh_kcmds[cmd])
    except (SSH_AUTH_ERROR, SSH_EXEC_ERROR, SSH_ERROR) as e:
        return _json_result(success=False, message=e.msg)

    _debug('json_exec_common',output)

    return _json_result(success=True, message="\n".join(output))



def json_exec_nfs(server, cmd):
    """
    Command executed to all NFS servers.
    Limited to ssh_kcmds.keys(). No arbitrary code allow

    Args:
        server: the server name in main_nfs_servers
        cmd: command ID for a list of command to execute on server

    Returns:
        dict like in _json_result used by bottle template
    """

    ssh_kcmds = {
        'check_home_perm': 'ls -ld %s',
        'check_home_doct': 'ls -ld %s',
        'check_home_temp': 'ls -ld %s',
        'nfsstat': 'nfsstat -3sn head -n +1',
        'quota_home_perm': 'repquota -u %s | awk \'{if (NF==8 && $1!="***" && $1!="Block") print}\'|sort -k3 -nr|head -10',
        'quota_home_doct': 'repquota -u %s | awk \'{if (NF==8 && $1!="***" && $1!="Block") print}\'|sort -k3 -nr|head -10',
        'quota_home_temp': 'repquota -u %s | awk \'{if (NF==8 && $1!="***" && $1!="Block") print}\'|sort -k3 -nr|head -10',
        'quota_total': 'repquota -ua | awk \'{if (NF==8 && $1!="***" && $1!="Block") print}\'|sort -k3 -nr|head -30',
    }

    host = ''
    user = 'root'
    real_cmd = ''

    for se in main_nfs_servers:
        if 'name' in se and se['name'] == server:
            host = se['host']
            nfs_server = se
            break

    # check host/server
    if not host or not server:
        return _json_result(success=False, message='Serveur "%s" inconnu' % server)

    # chech cmd
    if cmd not in ssh_kcmds:
        return _json_result(success=False, message='Commande interdite')


    ### pre-action cmd
    if cmd.find('check') != -1:
        _path = nfs_server[cmd[6:]].rstrip('/')
        _debug('json_exec_nfs/_path',_path)
        real_cmd = ssh_kcmds[cmd] % _path

    elif cmd == 'quota_total':
        real_cmd = ssh_kcmds[cmd]
        
    elif cmd.find('quota') != -1:
        _path = nfs_server[cmd[6:]].rstrip('/')
        _path_save = _path
        _debug('json_exec_nfs/_path',_path)
        # calculate mount point related to _path
        try:
            _path = _mount_point_rel_path(host,user,_path)
        except (SSH_EXEC_ERROR, SSH_AUTH_ERROR, SSH_EXEC_ERROR, SSH_ERROR) as e:
            return _json_result(success=False, message=e.msg)
        if _path is None:
            return _json_result(success=False, message='Pas de montage pour %s' % _path_save)
        real_cmd = ssh_kcmds[cmd] % _path

    elif cmd == 'nfsstat':
        real_cmd = ssh_kcmds[cmd]

    _debug('json_exec_nfs/real_cmd',real_cmd)

    try: 
        output = _ssh_exec(host, user, [real_cmd])
    except SSH_EXEC_ERROR as e:
        return _json_result(success=False, message="Erreur d'execution")
    except (SSH_AUTH_ERROR, SSH_EXEC_ERROR, SSH_ERROR) as e:
        return _json_result(success=False, message=e.msg)

    ### post-action cmd
    if cmd.find('check') != -1:
        message = 'OK'
    elif cmd == 'quota_total':
        sizes = {}
        for line in output:
            (login, mode, size, rest) = line.split(None, 3)
            if login == 'root': continue
            if login in sizes:
                sizes[login] += int(size)
            else:
                sizes[login] = int(size)
        # sort the dict related to value
        sorted_sizes = sorted(sizes.iteritems(), key=lambda (k,v): v, reverse=True)
        _debug('json_exec_nfs/sorted_sizes', sorted_sizes)
        _debug('json_exec_nfs/len(sorted_sizes)', len(sorted_sizes))
        # get only login > 10 Go
        limit = 10 * 1024 * 1024
        sorted_sizes_10G = filter(lambda (k,v): v > limit, sorted_sizes )
        if len(sorted_sizes_10G) > 1:
            message = ['Top 30 users > 10Go %s' % server]
            message += sorted_sizes_10G
        else:
            message = ['Top 30 users %s' % server]
            message += sorted_sizes
                
    elif cmd.find('quota') != -1:
        #_debug('ouput',output)
        message = ['Top 10 users %s:%s' % (server, _path)]
        for line in output:
            (login, mode, size, rest) = line.split(None, 3)
            if login == 'root': continue
            #_debug('line: ',login+'|'+size)
            message.append((login, size))
    else:
        message = output

    #_debug('json_exec_common/message',message)

    return _json_result(success=True, message=message)
        
def _ssh_exec(host, user, list_cmds):
    """
    High Level exec list of command with ssh
    """
    _debug('_ssh_exec(%s, %s, %s)' % (host, user, list_cmds))
    return _ssh_exec_paramiko(host, user, list_cmds)

def _ssh_exec_paramiko (host, user, list_cmds):
    """
    Low Level exec list of command with ssh
    paramiko implementation of _ssh_exec - easy way

    Args: 
        host, user: the parameters user@host for ssh
        list_cmds: list of commands to execute to the server
    
    Returns: 
        a list of string (stdout) commands result
    
    Raises:
        ERROR(msg) when host or user not valid
        SSH_AUTH_ERROR when paramiko.BadHostKeyException, paramiko.AuthenticationException
        SSH_EXEC_ERROR(msg) when ssh.exec_command return a none empty stderr stream
    """
    _debug('_ssh_exec_paramiko(%s, %s, %s)' % (host, user, list_cmds))
    if not host or not user or len(list_cmds) == 0:
        raise ERROR('host or user not valid')

    if bottle.DEBUG:
        paramiko.util.log_to_file('paramiko.log')

    ### client SSH
    ssh = paramiko.SSHClient()

    ### known_hosts
    ssh.load_system_host_keys()
    ssh.load_host_keys(os.path.expanduser('~/.ssh/known_hosts'))


    ### connection
    #ssh.connect(host, username='root', password='', pkey=private_key)
    try:
        ssh.connect(host, username='root', password='', key_filename=os.path.expanduser('id_rsa') )
    except paramiko.BadHostKeyException, paramiko.AuthenticationException:
        _debug('_ssh_exec_paramiko','connection to %s with `id_rsa` ... FAILED' % host)
        try:
            ssh.connect(host, username='root', password='', key_filename=os.path.expanduser('~/.ssh/id_rsa') )
        except paramiko.BadHostKeyException, paramiko.AuthenticationException:
            _debug('_ssh_exec_paramiko','connection to %s with `~/.ssh/id_rsa` ... FAILED' % host)
            raise SSH_AUTH_ERROR('Can not connect to host %s. You need to set a public key' % host)

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
            _debug('_ssh_exec_paramiko/exec cmd(%s)/sdterr' % cmd, 'OK')
            pass

        # rstripe \n on stdout
        for o in stdout.readlines():
            if o.endswith('\n'):
                o = o[:-1]
            list_out.append(o)

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
    
def _ssh_setquota(host,login,path,soft=0,hard=0):
    """
    Define a user quota on path as 'soft hard 0 0'

    return True if OK
    """
    if not host or not login or not path:
        return False

    mount = _mount_point_rel_path(host,user,path)

    cmd = 'setquota -u ' + login + ' %d %d 0 0 %s' % (soft, hard, mount) 
    _debug('_ssh_setquota(%s, %s, %s, %d, %d)' % (host, login, mount, soft, hard), 'cmd=%s' % cmd)

    try:
        _ssh_exec(host,'root', [cmd])
    except SSH_EXEC_ERROR:
        return False

    return True


def _mount_point_rel_path(host, user, path):
    """
    calculate mount point related to path

    Args: 
        path: the beginning of the search walk

    Returns:
        the finding mount point parent to the path
        or None if not found

    Raises:
        SEE _ssh_exec
    """
    mounts = _ssh_exec(host, user, ["cat /proc/mounts |awk '{print $2}'|sort -ur"])
    resu = path
    ok = False

    for mount in mounts:
        if mount == path:
            _debug('json_exec_nfs','mount point found: %s' % mount)
            ok = True
            break
            
        if os.path.commonprefix([mount, path]) == mount:
            resu = mount
            _debug('json_exec_nfs','sub mount point found: %s' % mount)
            ok = True
            break
    if ok:
        return resu
    else:
        return None

def _mongodb(actor, action, text):
    """
    Add log to mongoDB
    Args:
        logtext: text to add in DB

    Returns:
        None

    Raises:
        MONGODB_ERROR
    """
    pass



#----------------------------------------------------------
# Public Functions
#----------------------------------------------------------

def load_config(filename):
    """
    Load main config file
    Args:
        filename: ini file containing all the configuration

    Returns:
        sys.exit() if filename no exists

    """
    global main_ldap_servers, main_ldap_servers_name
    global main_nfs_servers, main_nfs_servers_name
    global main_admins

    _debug('Loading Global configuration file "'+filename+'" ...')

    config = ConfigParser.RawConfigParser()

    # section [admin-xxxxx]
    admin_attrs = {
        'ip': '<ip>',
        'name': '<username>'
    }
    
    # section [ldap-xxxxx]
    ldap_attrs = {
        'name': '<server name>', 
        'host': '<server URL>', 
        'port': '<server port> OPTIONAL', 
        'basedn': '<base DN>', 
        'basegroup': '<DN of groupOfUniqueNames>', 
        'baseuser': '<DN of groupOfUniqueNames>', 
        'binddn': '<DN for bind()>', 
        'bindpwd': '<password for bind()>'
    }

    # section [nfs-xxxxx]
    nfs_attrs = {
        'name': '<server name>', 
        'host': '<server URL>', 
        'home_perm' : '<absolute path to permanents home>',
        'home_doct' : '<absolute path to doctorants home>',
        'home_temp' : '<absolute path to temporaires home>'
    }

    def usage():
        print '#The syntax for the Global Configuration File is:'

        def d(t, d):
            print '[' + _colors.OKGREEN + t + _colors.NOCOLOR + ']'
            ks = d.keys()
            ks.sort()
            for k in ks:
                print k + ' = ' + _colors.OKGREEN + d[k] + _colors.NOCOLOR
            print ''
                
        d('admin-<id>', admin_attrs)
        d('ldap-<server id>', ldap_attrs)
        d('nfs-<server_id>', nfs_attrs)

    def check_dict(datas, models):
        sec_err = 0
        for k in models.keys():
            if k not in datas or not datas[k]:
                print _colors.WARNING + 'Configuration File "%s":' % filename + _colors.NOCOLOR + ' missing "%s=" on section [%s]' % (k, sec) 
                sec_err += 1
        if sec_err == 0:
            _debug('    section syntax OK')
            resu = True
        else:
            _debug('    section syntax ERROR: skip')
            print _colors.WARNING + "section [%s] not loaded" % sec + _colors.NOCOLOR
            resu = False

        return resu

        

    config.read(filename)

    if not os.path.isfile(filename):
        print _colors.FAIL + 'Configuration File "%s" does not exists' % filename + _colors.NOCOLOR
        usage()
        sys.exit(1)

    sections = config.sections()
    if len(sections) == 0:
        print _colors.FAIL + 'no section in file \'%s\'' % os.path.abspath(filename) + _colors.NOCOLOR
        usage()
        sys.exit(1)
   
    sec_errors = 0
    for sec in sections:
        if not sec: 
            continue

        _dict = dict(config.items(sec))
        _debug('... section ['+sec+']',_dict)
        if sec[:5] == 'admin':
            if check_dict(_dict, admin_attrs):
                main_admins.append(_dict)
            else:
                print _colors.WARNING + "section [%s] not loaded : No ADMIN section" % sec + _colors.NOCOLOR
                sec_errors += 1
            _debug('     section admin found',_dict)

        elif sec[:3] == 'nfs':
            if check_dict(_dict, nfs_attrs):
                main_nfs_servers.append(_dict)
            else:
                print _colors.WARNING + "section [%s] not loaded : No NFS section" % sec + _colors.NOCOLOR
                sec_errors += 1

        elif sec[:4] == 'ldap':
            if 'port' not in _dict or not _dict['port']: 
                _dict['port'] = 389
            if check_dict(_dict, ldap_attrs):
                main_ldap_servers.append(_dict)
            else:
                print _colors.WARNING + "section [%s] not loaded : No LDAP section" % sec + _colors.NOCOLOR
                sec_errors += 1

        else:
            print _colors.WARNING + "section [%s] not loaded : unknown type" % sec + _colors.NOCOLOR
            sec_errors += 1


    if sec_errors != 0:
        usage()
        print _colors.WARNING + 'Configuration file "%s" loaded but skip %d section(s)' % (filename, sec_errors) + _colors.NOCOLOR
    else:
        print _colors.OKGREEN + 'Configuration file "%s" loaded' % filename + _colors.NOCOLOR

        
    _debug('main_admins',main_admins)
    main_ldap_servers_name = [se['name'] for se in main_ldap_servers]
    _debug('main_ldap_servers:',main_ldap_servers)
    main_nfs_servers_name = [se['name'] for se in main_nfs_servers]
    _debug('main_nfs_servers:',main_nfs_servers)

    if len(main_ldap_servers_name) == 0:
        print _colors.FAIL + 'Configuration syntax error:' + _colors.NOCOLOR + 'on file ' + filename
        sys.exit(1)



def nfs_load_config(filename):
    """
    Load the file and set the GLOBAL VAR main_nfs_servers
    """
    global main_nfs_servers, main_nfs_servers_name

    _debug('Loading NFS configuration file "'+filename+'" ...')

    config = ConfigParser.RawConfigParser()
    config_attrs = {
        'name': '<server name>', 
        'host': '<server URL>', 
        'home_perm' : '<absolute path to permanents home>',
        'home_doct' : '<absolute path to doctorants home>',
        'home_temp' : '<absolute path to temporaires home>'
    }

    def usage():
        print
        print '#The syntax for the configuration file is:'
        print '[' + _colors.OKGREEN + '<server_id>' + _colors.NOCOLOR + ']'

        def t(name, text):
            print name + ' = ' + _colors.OKGREEN + text + _colors.NOCOLOR
    
        _keys_sorted = config_attrs.keys()
        _keys_sorted.sort()

        for k in _keys_sorted:
            t(k,config_attrs[k])

    config.read(filename)

    if not os.path.isfile(filename):
        print _colors.FAIL + 'Configuration File "%s" does not exists' % filename + _colors.NOCOLOR
        usage()
        sys.exit(1)

    sections = config.sections()
    if len(sections) == 0:
        print _colors.FAIL + 'no section in file \'%s\'' % os.path.abspath(filename) + _colors.NOCOLOR
        usage()
        sys.exit(1)
    
    for sec in sections:
        if not sec: continue
        _debug('... section ['+sec+'] ... ')
        _dict = dict(config.items(sec))
        for k in config_attrs.keys():
            if k not in _dict:
                print _colors.FAIL + 'Configuration File "%s" missing %s' % (filename, k) + _colors.NOCOLOR
                usage()
                sys.exit(1)
        _debug('    section syntax OK')
        
        main_nfs_servers.append(_dict)
        
    main_nfs_servers_name = [se['name'] for se in main_nfs_servers]
    _debug('main_nfs_servers:',main_nfs_servers)





def ldap_load_config(filename):
    """
    Load the file and set the GLOBAL VAR main_ldap_servers
    """
    global main_ldap_servers, main_ldap_servers_name

    _debug('Loading LDAP configuration file "'+filename+'" ...')

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
        print '[' + _colors.OKGREEN + '<server_id>' + _colors.NOCOLOR + ']'

        def t(name, text):
            print name + ' = ' + _colors.OKGREEN + text + _colors.NOCOLOR
    
        _keys_sorted = config_attrs.keys()
        _keys_sorted.sort()

        for k in _keys_sorted:
            t(k,config_attrs[k])

    config.read(filename)

    if not os.path.isfile(filename):
        print _colors.FAIL + 'Configuration File "%s" does not exists' % filename + _colors.NOCOLOR
        usage()
        sys.exit(1)

    sections = config.sections()
    if len(sections) == 0:
        print _colors.FAIL + 'no section in file \'%s\'' % os.path.abspath(filename) + _colors.NOCOLOR
        usage()
        sys.exit(1)
   
    sec_errors = 0
    for sec in sections:
        if not sec: 
            continue
        _debug('... section ['+sec+']')
        _dict = dict(config.items(sec))
        if 'port' not in _dict or not _dict['port']: _dict['port'] = 389
        sec_err = 0
        for k in config_attrs.keys():
            if k not in _dict or not _dict[k]:
                print _colors.WARNING + 'Configuration File "%s":' % filename + _colors.NOCOLOR + ' missing "%s=" on section [%s]' % (k, sec) 
                sec_errors += 1
                sec_err += 1
        if sec_err == 0:
            _debug('    section syntax OK')
            main_ldap_servers.append(_dict)
        else:
            _debug('    section syntax ERROR: skip')
            print _colors.WARNING + "section [%s] not loaded" % sec + _colors.NOCOLOR

    if sec_errors != 0:
        usage()
    else:
        print _colors.OKGREEN + 'Configuration file "%s" loaded' % filename + _colors.NOCOLOR

        
    main_ldap_servers_name = [se['name'] for se in main_ldap_servers]
    #_debug('main_ldap_servers:',main_ldap_servers)

    if len(main_ldap_servers_name) == 0:
        print _colors.FAIL + 'Configuration syntax error:' + _colors.NOCOLOR + 'on file ' + filename
        sys.exit(1)

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
    _filters = list_filters
    if 'objectClass=groupOfUniqueNames' not in list_filters:
        _filters.append('objectClass=groupOfUniqueNames')

    _debug('ldap_groups/list_filters',_filters)

    return _ldap_search(base, list_filters=_filters, list_attrs=list_attrs)
    
   
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

@bottle.route('/static/<filepath:path>')
def static(filepath):
    return bottle.static_file(filepath, root=os.path.join('.', 'static'))


@bottle.route('/')
@bottle.view('index')
def index():
    _debug_route()
    return _dict(news=main_news)

@bottle.route('/servers')
@bottle.view('servers')
def servers():
    _debug_route()
    return _dict(ldap_servers=main_ldap_servers_name, 
        nfs_servers=main_nfs_servers_name,
        common_cmds=['uname', 'issue'],
        ldap_cmds=[],
        nfs_cmds=['check_home_perm', 'check_home_doct', 'check_home_temp','nfsstat'],
        )

@bottle.route('/server_ldap/<server>')
def server_ldap(server=None):
    """print LDAP server information
    use mulpiple template : 
    * server_ldap : for good request
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
                return bottle.template('servers', _dict(warn='LDAP server "%s" connexion error' 
                    % server, servers=main_ldap_servers_name))
            return bottle.template('server_ldap', _dict(name=se['name'], server=se))

    return bottle.template('servers', _dict(warn='LDAP server "%s" not found' % server, servers=main_ldap_servers_name))

@bottle.route('/server_nfs/<server>')
def server_nfs(server=None):
    """print LDAP server information
    use multiple template : 
    * server_nfs : for good request
    * servers : for warning redirection
    """
    _debug_route()
    for se in main_nfs_servers:
        if 'name' not in se:
            _debug('server_attr/se[name]','Dont exists !!')
            continue
        if se['name'] == server:
            return bottle.template('server_nfs', _dict(name=se['name'], server=se))

    return bottle.template('servers', 
        _dict(warn='NFS server "%s" not found' % server, 
        ldap_servers=main_ldap_servers_name, 
        nfs_servers=main_nfs_servers_name))

@bottle.route('/groups')
@bottle.view('groups')
def groups():
    _debug_route()
    ldap_initialize()
    groups = ldap_groups(list_attrs=['cn','description'])
    ldap_close()
    if groups is None:
        return _dict(warn='LDAP main server "%s" error' % main_ldap_server['name'], groups={})
    return _dict(groups=groups)

@bottle.route('/group/<group>')
@bottle.view('group')
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


@bottle.route('/users/search/<str_filter>')
@bottle.view('users_search')
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
        #_list_filters.append('%s=*%s*' % (st, _filter))
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

@bottle.route('/users')
@bottle.route('/users/<type>')
@bottle.view('users_type')
def users_type(type=None):
    _debug_route()
    
    if type is None:
        type = '*'

    if type not in main_users.keys():
        bottle.redirect('/users/*')

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
    return _dict(title=title, users=users, nfs_servers=main_nfs_servers_name)


@bottle.route('/user/<uid>')
@bottle.view('user')
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

@bottle.route('/news')
@bottle.route('/news/<ver>')
@bottle.view('news')
def news(ver=None):
    _debug_route()
    return _dict(ver=ver, news=main_news)



@bottle.route('/about')
@bottle.view('about')
def about():
    _debug_route()
    return _dict(warn=None, ldap_ver=ldap.__version__, bottle_ver=bottle.__version__)

#----------------------------------------------------------
# Routing JSON Functions

@bottle.route('/api/useradd', method='POST')
def json_useradd():
    """
    add user and return the uid of the new user
    or None on error

    Mandatory fields passed in POST: 
    'cn', 'sn', 'givenName', 'mail', 'description', 'usertype', 'hostname'
    
    Mandatory fields for usertype == p:
    'group'

    Mandatory fields for usertype == t or d:
    'manager'

    Optional fields:
    'uid'

    """
    _debug_route()
    datas = bottle.request.params
    ldap_data = {}

    ### LDAP operations

    # mandatory/LDAP attrs
    for attr in ['cn', 'sn', 'givenName', 'mail', 'description']:
        if attr not in datas or not datas[attr]:
            return _json_result(success=False, message='missing mandatory/LDAP parameter: '+attr)
        ldap_data[attr] = [datas[attr]]
        # add local variable: `attr` = datas[attr]
        

    # mandatory/none LDAP attrs
    for attr in ['usertype', 'hostname']:
        if attr not in datas or not datas[attr]:
            return _json_result(success=False, message='missing mandatory/none LDAP parameter: '+attr)
        else:
            _debug(attr,datas[attr])
            
    usertype = datas['usertype']
    hostname = datas['hostname']

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
        _t = _ldap_new_posixAccount(usertype, uid, hostname)
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
        _ldap_useradd(dn, ldap_data)
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
    nfs_server_hostname = ''
    for n in main_nfs_servers:
        if n['name'] == hostname:
            nfs_server_hostname = n['host']
    if not nfs_server_hostname:
        return _json_result(success=False, message='Cant find NFS')

    for text, cmd in [
        ('creation du HOME par copie des fichiers /etc/skel','cp -r /etc/skel %s' % homeDirectory),
        (u'changement du propriétaire','chown -R %s:%s %s' % (uidNumber, gidNumber, homeDirectory)),
        ('changement des droits','chmod -R u=rwX,go= %s' % homeDirectory),
        ]:
        _debug('json_useradd/Try to exec %s [%s]' % (cmd, text))
        try:
            _ssh_exec(nfs_server_hostname,'root',[cmd])
        except SSH_EXEC_ERROR as e:
            return _json_result(success=False, message=e.msg)
        _debug('json_useradd/Try to exec %s' % cmd, 'OK')

    
    if not _ssh_setquota(nfs_server_hostname, 
            uid, 
            homeDirectory,
            main_users[usertype]['quotasoft'], 
            main_users[usertype]['quotahard']) :
        return _json_result(success=False, message='erreur de Quota')

            
    return _json_result(success=True, uid=uid, userPassword=userPassword, message=u'répertoire crée, droits changés, quotas appliqués')

@bottle.route('/api/userdel', method='POST')
def json_userdel():
    _debug_route()
    datas = bottle.request.params
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
            
    # TODO : check if user have students

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

@bottle.route('/api/user/<uid>/attr/<attr>', method='POST')
def json_user_set_attr(uid,attr):
    """
    Set user attr with POST method
    """
    _debug_route()
    datas = bottle.request.params
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



@bottle.route('/api/user/<uid>/attr/<attr>')
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


@bottle.route('/api/groups')
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

@bottle.route('/api/autocomplete_manager')
def json_autocomplete_manager():
    """
    search for permanents user with 
    term=<search string>
    """
    _debug_route()
    datas = bottle.request.params
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


@bottle.route('/api/server/<server>/issue')
def json_server_issue(server):
    _debug_route()
    return json_exec_common(server,'issue')

@bottle.route('/api/server/<server>/uname')
def json_server_uname(server):
    _debug_route()
    return json_exec_common(server,'uname')

@bottle.route('/api/server_nfs/<server>/check_home_perm')
def json_server_nfs_check_home_perm(server):
    _debug_route()
    return json_exec_nfs(server,'check_home_perm')

@bottle.route('/api/server_nfs/<server>/check_home_doct')
def json_server_nfs_check_home_doct(server):
    _debug_route()
    return json_exec_nfs(server,'check_home_doct')

@bottle.route('/api/server_nfs/<server>/check_home_temp')
def json_server_nfs_check_home_temp(server):
    _debug_route()
    return json_exec_nfs(server,'check_home_temp')

@bottle.route('/api/server_nfs/<server>/nfsstat')
def json_server_nfs_nfsstat(server):
    _debug_route()
    return json_exec_nfs(server,'nfsstat')

@bottle.route('/api/server_nfs/<server>/quota_home_perm')
def json_server_nfs_quota_home_perm(server):
    _debug_route()
    return json_exec_nfs(server,'quota_home_perm')

@bottle.route('/api/server_nfs/<server>/quota_home_doct')
def json_server_nfs_quota_home_doct(server):
    _debug_route()
    return json_exec_nfs(server,'quota_home_doct')

@bottle.route('/api/server_nfs/<server>/quota_home_temp')
def json_server_nfs_quota_home_temp(server):
    _debug_route()
    return json_exec_nfs(server,'quota_home_temp')

@bottle.route('/api/server_nfs/<server>/quota_total')
def json_server_nfs_quota_total(server):
    _debug_route()
    return json_exec_nfs(server,'quota_total')


#----------------------------------------------------------
# MAIN

if __name__ == '__main__':

    #----------------------------------------------------------
    # DEBUG MODE/PRODUCTION
    #----------------------------------------------------------
    bottle.debug(True)
    #----------------------------------------------------------
    for m in [bottle, ldap, paramiko]:
        _modules_version(m)

    load_config('config.ini')

    main_nav = [ 
        ('/', 'accueil'), 
        ('*', 'serveurs'), 
        ('/servers', 'tableau de bord'), 
        ('/server_ldap/'+main_ldap_servers_name[0], 'master ldap'), 
        ('',''), 
        ('*', 'personnels'),
        ('_SEARCH_','rechercher...'),
        ('/users/p',main_users['p']['name']),
        ('/users/d',main_users['d']['name']),
        ('/users/t',main_users['t']['name']),
        ('',''), 
        ('*', 'structure'),
        ('/groups','les équipes'),
        ('/users','les utilisateurs'),
        ('',''), 
        ('*', 'site web'), 
        ('/news', 'news') , 
        ('/about', 'à propos')
        ]
    if bottle.DEBUG:
        port = 8888
        reloader = True
        print _colors.OKBLUE + 'mode DEBUG' + _colors.NOCOLOR
    else:
        port = 8080
        reloader = False
        
    bottle.run(host='0.0.0.0', port=port, reloader=reloader, debug=bottle.DEBUG)


# vim:spelllang=en:
