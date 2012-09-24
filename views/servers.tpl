%rebase base title="serveurs LDAP", nav=nav, warn=warn, author=author, version=version
<div class="box shadow">
<h1>Liste des Serveurs</h1>
    <ul>
    %for s in servers:
        <li><a href="/server/{{s}}">{{s}}</a>. <input type="button" id="{{s}}" value="test connexion" onclick="alert('Not Yet Implemented')"/></li>
    %end
    </ul>
</div>

