%rebase base title="Équipes : %s" % cn , nav=nav, warn=warn, author=author, version=version


<script type="text/javascript">
<!-- 
$(function() {
    // click on load
    log_on_click($('#addlogd'), '/api/log/group/{{cn}}', $('#logs-texts'));
    
});
// -->
</script>

<div id="onglets">
    <ul>
    <li><a href="#page" class="actif nav">fiche</a></li>
    <!-- li><a href="#fiche" class="nav">édition</a></li -->
    <li><a href="#logs" class="nav">logs</a></li>
    </ul>

    <div id="page" class="onglet box shadow">

    <h1>{{desc}}</h1>
    <dt>
        %if desc:
        <dt>Description</dt>
        <dd>{{desc}}</dd>
        %end

        <dt>{{len(members)}} membres</dt>
        %for u in members:
        <dd><a href="/user/{{u['uid']}}">{{u['cn']}}</a></dd>
        %end
    </dt>
    </div><!-- #page -->

    <div id="logs" class="onglet box shadow">
        <h1 id="heading">fiche LOGS : {{desc}}</h1>
        <div>Liste chronologique des logs.</div>
        <button id="addlogd">mettre a jour les logs</button>
        <div id="logs-texts"> </div>
    </div><!-- #logs -->

</div><!-- #onglets -->
