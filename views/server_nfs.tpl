%rebase base title="serveur NFS : %s" % name, nav=nav, warn=warn, author=author, version=version
<script src="/static/raphael-min.js"></script>
<script src="/static/raphael.pie.js"></script>
<script type="text/javascript">
<!--
$(function() {

    function ajax_button_graph(pie, span, url){
        span.addClass('ui-autocomplete-loading').html('&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;');
        pie.hide('slow');
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
                        sizes = []
                        title = response['message'][0];
                    // /!\ the first element of response[message] is the title: do not include to the dirty hack loop
                    for( var i = 1, ii = response['message'].length; i < ii; i++) {
                        var login = response['message'][i][0],
                            size = response['message'][i][1];
                        logins.push(login);
                        sizes.push(parseInt(size, 10));
                        };
                    // Must be BEFORE Raphael - draw
                    pie.show('slow');
                    // (re)plot pie
                    Raphael("pie", 400, 400).pieChart(200, 200, 133, sizes, logins, title);
                } else {
                    span.text('Pas de quota');
                }
                },
            error: function(xhr, textStatus, error){
                span.removeClass('ui-autocomplete-loading').text('');
                show_warning('Server error: '+error);
                },
            });
    };
    $('button#issue').click(function() { ajax_button_span_url($(this), $(this).next(), '/api/server/{{name}}/issue') });
    $('button#uname').click(function() { ajax_button_span_url($(this), $(this).next(), '/api/server/{{name}}/uname') });
    $('button#all').click(function() { 
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
<h1>serveur <span id="server" class="nfs">{{name}}</span></h1>
<h3>Données</h3>
<ul>
    %for item in ['host', 'home_perm', 'home_doct', 'home_temp']:
        %if item not in server:
            %continue
        %end
    <li>
        <strong>{{item}}</strong>: {{server[item]}}
        %if item.find('home_') != -1:
            <button id="check_{{item}}">check</button>
            <button id="quota_{{item}}">quota</button>
            <span id="{{item}}" class="term"></span>
        %else:
            <button id="quota_total">quota total</button>
            <span id="quota_total" class="term"></span>
        %end
    </li>
    %end
</ul>

    <div id="pie"></div>
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
    </ul>







</div><!-- box shadow -->

