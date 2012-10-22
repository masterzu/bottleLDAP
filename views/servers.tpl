%rebase base title="Tableau de Bord", nav=nav, warn=warn, author=author, version=version
<script type="text/javascript">
<!--

/*
$(function() {
});
*/

// -->
</script>

<div class="box shadow">
<h1>Liste des Serveurs</h1>

    <h2>Serveur LDAP</h2>
    <ul>
    %for s in ldap_servers:
        <li><a href="/server_ldap/{{s}}" class="server ldap">{{s}}</a></li>
    %end
        <li class="noserver"></li>
    </ul>
    <h2>Serveurs NFS</h2>
    <ul>
    %for s in nfs_servers:
        <li><a href="/server_nfs/{{s}}" class="server nfs">{{s}}</a></li>
    %end
        <li class="noserver"></li>
    </ul>
</div>

