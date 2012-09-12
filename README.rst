==========
bottleLDAP
==========

:Author: Patrick Cao Huu Thien
:Date: 29 juin 2011
:Revision: 1

:abstract: 

    Ce document présente le site web bottleLDAP

.. #################################
   definition des roles persos
   http://docutils.sourceforge.net/docs/ref/rst/roles.html#raw
.. default-role:: strong
.. role:: raw-html(raw)
   :format: html

.. #################################
   table des matieres 
   (ne pas oublier l'espace final)
.. contents:: Le Sommaire

Présentation générale
=====================

Ce site a un double objectif: Faire de moi un ubergeek en `Python <http://www.python.org>`_, `CSS` et autre webdesign. 
Et en plus,, accessoirement, pouvoir administrer le serveur LDAP de l'Institut.

Ce site est donc programmé entièrement en Python, avec l'aide de la micro web-framework `bottlepy <http://bottlepy.org/>`_ et de la librairie `python-ldap <http://www.python-ldap.org/>`_



Démarrage du serveur
====================

Pour démarrer le serveur, il faut :

#. créer une fichier `ldap_servers.ini` contenant les informations suivantes::

    [<serveur_id>]
    name = <server name>
    host = <fqhn>
    port = <optional>
    basedn = <ldap base DN>
    basegroup = <DN of the groupOfUniqueNames>
    baseuser = <DN of the groupOfUniqueNames>
    binddn = <DN to bind>
    bindpwd = <password of %(binddn)s>

#. copier le fichier de clé privée `id_rsa` pour permettre d'avoir un accès ``root`` au serveur NFS

#. Puis dans une console, taper la commande::

    $ python server.py
    Bottle server starting up (using WSGIRefServer())...
    Listening on http://localhost:8080/
    Use Ctrl-C to quit.

.. vim:set spelllang=fr:
