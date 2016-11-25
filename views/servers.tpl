%rebase base title="Tableau de Bord", nav=nav, warn=warn, author=author, version=version
%#
%# Vars: ldap_servers
%#
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

<h3 class="ldap">LDAP</h3>
<ul class="inline">
    %for s in ldap_servers:
    <li><a href="/server_ldap/{{s}}" class="server ldap btn">{{s}}</a></li>
    %end
</ul>
<h3 class="nfs">NFS</h3>
    <ul class="inline">
        %for s in nfs_servers:
        <li><a href="/server_nfs/{{s}}" class="btn server nfs">{{s}}</a></li>
        %end
    </ul>
</div>

<!-- :vim:ft=html: -->
