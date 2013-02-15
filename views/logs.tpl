%rebase base title="Logs", nav=nav, warn=warn, author=author, version=version


<script type="text/javascript">
<!-- 
$(function() {

    // click on load
    log_on_click($('#button_users'), '/api/log/users', $('#logs_users'));
    log_on_click($('#button_groups'), '/api/log/groups', $('#logs_groups'));
});
// -->
</script>

<div id="onglets">
    <ul>
    <li><a href="#users" class="actif nav">Utilisateurs</a></li>
    <li><a href="#groups" class="nav">Groupes</a></li>
    </ul>

    <div id="users" class="onglet box shadow">
        <h1 id="heading">Logs Utilisateur</h1>
        <div>Liste anti-chronologique des logs utilisateurs.</div>
        <button id="button_users">afficher les logs</button>
        <div id="logs_users"> </div>
    </div><!-- #users -->

    <div id="groups" class="onglet box shadow">
        <h1 id="heading">Logs Groups</h1>
        <div>Liste anti-chronologique des logs groupes.</div>
        <button id="button_groups">afficher les logs</button>
        <div id="logs_groups"> </div>
    </div><!-- #groups -->

</div><!-- #onglets -->
