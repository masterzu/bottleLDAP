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

    <h2 class="ldap">LDAP</h2>
    <ul class="inline">
    %for s in ldap_servers:
        <li><a href="/server_ldap/{{s}}" class="server ldap btn">{{s}}</a></li>
    %end
    </ul>
    <h2 class="nfs">NFS</h2>
    <ul class="inline">
    %for s in nfs_servers:
        <li><a href="/server_nfs/{{s}}" class="btn server nfs">{{s}}</a></li>
    %end
    </ul>
</div>

