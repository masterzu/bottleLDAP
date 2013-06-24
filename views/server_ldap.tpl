%rebase base title="serveur LDAP : %s" % name, nav=nav, warn=warn, author=author, version=version

<script type="text/javascript">
<!--

$(function() {

    $('a#issue').click(function() { ajax_button_span_url($(this), $('span#issue'), '/api/server/{{name}}/issue') });
    $('a#uname').click(function() { ajax_button_span_url($(this), $('span#uname'), '/api/server/{{name}}/uname') });
    $('#all').click(function() { 
        ajax_button_span_url($(this), $('span#issue'), '/api/server/{{name}}/issue');
        ajax_button_span_url($(this), $('span#uname'), '/api/server/{{name}}/uname');
    });
});

// -->
</script>

<div class="box shadow">
<h1>serveur LDAP <span id="server" class="ldap">{{name}}</span></h1>
<h3>Données</h3>
<p>Données de connexion au serveur:</p>
<dl class="dl-horizontal">
    %for item in ['host', 'port', 'basedn', 'baseuser', 'basegroup']:
        %if item not in server:
            %continue
        %end
        <dt>{{item}}</dt>
        <dd>{{server[item]}}</dd>
    %end
</dl>

<h3>Actions</h3> 
<p>Informations diverses</p>
    <dl class="dl-horizontal">
        <dt> <a id="issue" class="btn btn-mini">issue</a> </dt>
        <dd> <span id="issue" class="term">&nbsp;</span> </dd>

        <dt> <a id="uname" class="btn btn-mini">uname</a> </dt>
        <dd> <span id="uname" class="term">&nbsp;</span> </dd>
    </dl>
    <dl class="dl-horizontal">
        <dt> <button id="all" class="btn btn-mini">toutes</button> </dt>
    </dl>
</div><!-- box shadow -->

