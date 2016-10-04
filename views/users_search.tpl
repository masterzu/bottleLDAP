%rebase base title="recherche d'utilisateur", nav=nav, warn=warn, author=author, version=version
<div class="box shadow">
<h1>Recherche utilisateur : {{query}}</h1>

<strong>Filtre LDAP</strong>: <pre>{{ldap_filter}}</pre>

<hr/>

%l = len(users)
<strong>Résultats</strong>: Il y a <strong>{{l}}</strong> réponses
<ol>
%for dn, u in users:
    <li><a href="/user/{{u['uid'][0]}}" title="{{dn}}">{{u['cn'][0]}}</a> ({{u['uid'][0]}})</li>
%end
</ol>
</div><!-- box shadow -->

<!-- :vim:ft=html: -->
