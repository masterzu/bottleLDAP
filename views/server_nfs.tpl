%rebase base title="serveur NFS : %s" % name, nav=nav, warn=warn, author=author, version=version
%#
%# Vars: server, name
%#
<script type="text/javascript">
<!--
$(function() {

    function ajax_button_graph(pie, span, url){
        span.addClass('ui-autocomplete-loading').html('&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;');
        pie.hide();
        $.ajax({
            url: url,
            type: "GET",
            dataType: "json",
            success: function(response){
                span.removeClass('ui-autocomplete-loading').text('');
                // empty all children of pie
                pie.empty();
                if (response['success']) {
                    //alert(response['message']);
                    var logins = [],
                        sizes = [],
                        quotas = [],
                        graces = [],
                        title = response['message'][0];
                    // /!\ the first element of response[message] is the title: do not include to the dirty hack loop
                    for( var i = 1, ii = response['message'].length; i < ii; i++) {
                        var login = response['message'][i][0],
                            size = response['message'][i][1],
                            quota = response['message'][i][2],
                            grace = response['message'][i][3];
                        logins.push(login);
                        sizes.push(parseInt(size, 10));
                        quotas.push(quota);
                        graces.push(grace);
                        };
                    // Must draw be BEFORE Raphael - draw
                    $('#pieblack').show();
                    pie.show();
                    // (re)plot pie
                    Raphael("pie", 400, 400).pieChart(200, 200, 133, sizes, logins, quotas, graces, title);
                    pie.center();
                } else {
                    span.text('Pas de quota');
                }
                },
            timeout: 2000,
            error: function(xhr, textStatus, error){
                span.removeClass('ui-autocomplete-loading').text('');
                if (textStatus=='timeout') {
                    show_warning('Serveur trop lent. Peut etre inaccessible ?');
                } else {
                    show_warning('Server error: '+error);
                }},
            });
    };
    $('a#issue').click(function() { 
        ajax_button_span_url($(this), $('span#issue'), '/api/server/{{name}}/issue');
    });
    $('a#uname').click(function() { 
        ajax_button_span_url($(this), $('span#uname'), '/api/server/{{name}}/uname');
    });
    $('button#all').click(function() { 
        %for c in ['home_perm', 'home_doct', 'home_temp']:
            ajax_button_span_url($('button#check_{{c}}'), null, '/api/server_nfs/{{name}}/check_{{c}}');
        %end
        ajax_button_span_url($(this), $('span#issue'), '/api/server/{{name}}/issue');
        ajax_button_span_url($(this), $('span#uname'), '/api/server/{{name}}/uname');
    });
    %for c in ['home_perm', 'home_doct', 'home_temp']:
        $('button#check_{{c}}').click(function() {ajax_button_span_url($(this), null, '/api/server_nfs/{{name}}/check_{{c}}') });
        $('button#quota_{{c}}').click(function() {ajax_button_graph($("#pie"), $(this).next(), '/api/server_nfs/{{name}}/quota_{{c}}') });
    %end

    $('button#quota_total').click(function() {ajax_button_graph($("#pie"), $(this).next(), '/api/server_nfs/{{name}}/quota_total') });





});
// -->
</script>

<div class="box shadow">
<h1>serveur NFS <span id="server" class="nfs">{{name}}</span></h1>
<h3>Données</h3>
<dl class="dl-horizontal">
    %for item in ['host', 'home_perm', 'home_doct', 'home_temp']:
        %if item not in server:
            %continue
        %end
        <dt>{{item}}</dt>
        <dd>{{server[item]}}</dd>
        <dd>
        %if item.find('home_') != -1:
            <button id="check_{{item}}" title="existence du repertoire" class="btn btn-mini">?</button>
            <button id="quota_{{item}}" title="camembert du Quota" class="btn btn-mini">quota</button>
            <span id="{{item}}" class="term"></span>
        %else:
            <button id="quota_total" title="camembert du Quota Total" class="btn btn-mini">quota total</button>
            <span id="quota_total" class="term"></span>
        %end
        </dd>

    <!-- <li> -->
    <!--     <strong>{{item}}</strong>: {{server[item]}} -->
    <!--     %if item.find('home_') != -1: -->
    <!--         <button id="check_{{item}}" title="existence du repertoire" class="btn btn-mini">?</button> -->
    <!--         <button id="quota_{{item}}" title="camembert du Quota" class="btn btn-mini">quota</button> -->
    <!--         <span id="{{item}}" class="term"></span> -->
    <!--     %else: -->
    <!--         <button id="quota_total" title="camembert du Quota Total" class="btn btn-mini">quota total</button> -->
    <!--         <span id="quota_total" class="term"></span> -->
    <!--     %end -->
    <!-- </li> -->
    %end
</dl>

    <div id="pieblack">
        <div id="pie"></div>
    </div>
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

<!-- :vim:ft=html: -->
