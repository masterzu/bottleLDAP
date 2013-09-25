==========
bottleLDAP
==========

:Author: Patrick Cao Huu Thien
:Date: dd mmmm 2013
:Version: devel

:abstract: 

    Ce document présente le projet **bottleLDAP**

.. #################################
   definition des roles persos
   http://docutils.sourceforge.net/docs/ref/rst/roles.html#raw
.. default-role:: strong
.. role:: raw-html(raw)
   :format: html

.. #################################
   table des matières 
   (ne pas oublier l'espace final)
.. contents:: Sommaire

Présentation générale
=====================

Ce projet a un double objectif.  
**Cuisiner** un site web **minimaliste** (*sans apache ou autre Guerrier du web*) en `Python <http://www.python.org>`_, `CSS <http://www.w3.org/Style/CSS/Overview.fr.html>`_ `JQuery <http://jquery.com/>`_ et autre ingrédients en *webdesign*. 
Un soupçon de `mongoDB <http://www.mongodb.org/>`_ à été récemment ajouté, juste pour le goût.

Et en plus, accessoirement, pouvoir **administrer** le serveur `LDAP <http://www.openldap.org/>`_ de l'Institut ``;-P``.

Ce site est donc entièrement concu en Python, avec l'aide de la micro web-framework `bottlepy <http://bottlepy.org/>`_ et de la librairie `python-ldap <http://www.python-ldap.org/>`_

Concernant la partie, client, c'est du JQuery avec une touche d'AJAX, une larme de `Raphaël JS <http://raphaeljs.com/>`_ le tout saupoudré de `bootstrap <http://twitter.github.io/>`_


Installation
============

Voir *INSTALL.rst*

Démarrage du serveur
====================

Pour démarrer le serveur, il faut :

* créer un fichier `config.ini` contenant les informations sur :

 * l' application::
    [main]
    port = <runnig port>
    debug = False (optional)

 * le serveur LDAP::

    [ldap-<serveur_id>]
    name = <server name>
    host = <fqhn>
    port = <optional>
    basedn = <ldap base DN>
    basegroup = <DN of the groupOfUniqueNames>
    baseuser = <DN of the groupOfUniqueNames>
    binddn = <DN to bind>
    bindpwd = <password of %(binddn)s>

 * les serveurs NFS::

    [nfs-<serveur_id>]
    name = <server name>
    host = <fqhn>
    home_perm = <absolute path to permanents home>
    home_doct = <absolute path to doctorants home>
    home_temp = <absolute path to temporaires home>

 * les administrateurs::

    [admin-<id>]
    ip = <ip>
    name = <name>


* copier le fichier de clé privée `id_rsa` pour permettre d'avoir un accès ``root`` aux serveurx NFS

* Puis dans une console, taper la commande::

    $ python server.py config.ini
    Bottle server starting up (using WSGIRefServer())...
    Listening on http://localhost:8080/
    Use Ctrl-C to quit.

.. vim:set spelllang=fr:
