
Installation
============

En PYTHON l'outil standard (et indépendant de toutes contrainte du système hôte) d'installation de paquet est `pip <http://www.pip-installer.org>`_. Il remplace l'ancien outils ``easy_install``.

virtualenv
----------

Le plus simple est de lancer le serveur dans un environnement `virtualenv <http://www.virtualenv.org/en/latest/#installation>`_. 

Ce script permet de pouvoir gérer un environnement PYTHON sans interférer avec le système hôte. 
L'environnement est installer dans le répertoire de votre choix et activé par un simple script (``/path/to/virtualenv/ofmychoice/bin/activate``).


* Installation de **virtualenv**.  
  Pour cela, il suffit d'installer **virtualenv** via l'outil standard (et indépendant de toutes contrainte du système hôte) ``pip``::

	$ pip install virtualenv
    Downloading/unpacking virtualenv
      Downloading virtualenv-1.9.1.tar.gz (2.0MB): 2.0MB downloaded
    ...
    Successfully installed virtualenv
    Cleaning up...

* Création de l'environnement::

  	$ virtualenv myenv
    Using real prefix '/usr'
    New python executable in myenv/bin/python
    Overwriting myenv/lib/python2.6/distutils/__init__.py with new content
    Installing setuptools............done.
    Installing pip...............done.

* Activation de l'environnement pour le shell courant::

  	$ source myenv/bin/activate

* Vérification::

  	$ pip --version
    pip 1.3.1 from /home/patrick/test/myenv/lib/python2.6/site-packages/pip-1.3.1-py2.6.egg (python 2.6)

Prérequis
---------

Le fichier *requirements.txt* permet de lister pour ``pip`` les modules à installer.
L'installation des modules se fait par un simple::

	$ pip install -r requirements.txt

Erreurs
_______

En cas de soucis, par exemple lorsque la compilation de paquets nécessitant d'autres fichiers sources, il faut lire les messages d'erreurs et ajouter les fichiers manquants au système.

Pour **Debian/Ubuntu** la marche a suivre est la suivante:

* lister les fichiers manquant::

  	$ pip install --upgrade -r requirements.txt |grep -i 'No such file'
    Modules/errors.h:8:18: error: lber.h: No such file or directory
    Modules/errors.h:9:18: error: ldap.h: No such file or directory
    ...


* chercher les fichiers::

  	$ apt-file search --regexp /lber.h$
    libldap2-dev: /usr/include/lber.h
	
    $ apt-file search --regexp /ldap.h$
    libldap2-dev: /usr/include/ldap.h
    libmailutils-dev: /usr/include/mailutils/ldap.h

* et installer les paquets correspondant::

    $ sudo apt-get install libldap2-dev

* et finalement relancer l'installation des prérequis::

  	$ pip install --upgrade -r requirements.txt

Production
==========

* changer la version dans les fichiers sources, par exemple la version **42**::

  $ make_release.sh 42

* copier les sources depuis la branche *master*::

  $ git archive -o prodiction-42.zip HEAD

* y ajouter la clé ssh *rsa_id* et le fichier de configuration *config.ini*

* *et voila !*
