%rebase base title="À Propos", nav=nav, warn=warn, author=author, version=version
%#
%# Vars: ldap_ver, bottle_ver, paramiko_ver
%#
<div class="box shadow">
<h1>À Propos</h1>

<p>Ce projet a un double objectif.
<strong>Cuisiner</strong> un site web <em>minimaliste</em> (sans apache ou autre <em>Guerrier du web</em>) et autre ingrédients en <em>webdesign</em>.
<p>Et accessoirement, pouvoir <strong>administrer</strong> le serveur <a class="reference external" href="http://www.openldap.org/">LDAP</a> de l'Institut <tt class="docutils literal"><span class="pre">;-P</span></tt>.</p>

<hr/>

<p>
	Les ingrédients de ce site sont <a class="reference external" href="http://www.python.org">Python</a> dans un enrobage de micro web-framework <a class="reference external" href="http://bottlepy.org/">bottlepy</a> (version {{bottle_ver}}) et des accompagnements <a class="reference external" href="http://www.python-ldap.org/">python-ldap</a> (version {{ldap_ver}}) et <a class="reference external" href="http://www.paramiko.org/">paramiko</a> (pour les connexions ssh &mdash; version {{paramiko_ver}}) et également <a class="reference external" href="http://www.mongodb.org/">MongoDB</a>.
</p>

<p>
	Les condiments (coté client) sont <a href="http://jquery.com/" target="_blank">JQuery</a>/<a class="reference external" href="http://www.w3.org/Style/CSS/Overview.fr.html">CSS</a> avec une touche d'<a href="http://fr.wikipedia.org/wiki/Ajax_(informatique)" target="_blank">AJAX</a>, une larme de <a href="http://raphaeljs.com/" target="_blank">Raphaël JS</a> le tout saupoudré de <a href="https://getbootstrap.com/" target="_blank">bootstrap</a>.
</p>

<p>
	Le tout est servi dans un plat <a class="reference external" href="https://www.docker.com/">Docker</a> sur un plateau <a class="reference external" href="https://www.proxmox.com/en/proxmox-ve">proxmox</a>.
</p>
</div>

<div class="box shadow">
<h1>Outils</h1>
<p>J'ai réussi, avec comme outils <a href="http://www.vim.org/" target="_blank">vim</a> et quelques <a href="http://fr.wikipedia.org/wiki/R%C3%A9flexe_de_flexion" target="_blank">doigts et neurones</a>, le tour de force de faire fonctionner ce site... <em>OUF !!</em></p>
</div>

<!-- :vim:ft=html: -->
