%rebase base title="serveur LDAP : %s" % name, nav=nav, warn=warn, author=author, version=version

<script type="text/javascript">
<!--

$(function() {

    $('button#issue').click(function() { ajax_button_span_url($(this), $(this).next(), '/api/server/{{name}}/issue') });
    $('button#uname').click(function() { ajax_button_span_url($(this), $(this).next(), '/api/server/{{name}}/uname') });
    $('button#all').click(function() { 
        ajax_button_span_url($(this), $('span#issue'), '/api/server/{{name}}/issue');
        ajax_button_span_url($(this), $('span#uname'), '/api/server/{{name}}/uname');
    });
});

// -->
</script>

<div class="box shadow">
<h1>serveur <span id="server" class="ldap">{{name}}</span></h1>
<h3>Données</h3>
<ul>
    %for item in ['host', 'port', 'basedn', 'baseuser', 'basegroup']:
        %if item not in server:
            %continue
        %end
    <li>
        <strong>{{item}}</strong>: {{server[item]}}
    </li>
    %end
</ul>

<h3>actions ssh</h3> 
    <ul>
        <li>
            <button id="issue" name="issue">issue</button>
            <span id="issue" class="term">&nbsp;</span>
        </li>
        <li>
            <button id="uname" name="uname">uname</button>
            <span id="uname" class="term">&nbsp;</span>
        </li>
        <hr/>
        <button id="all">toutes</button>
    <ul>
</div><!-- box shadow -->

