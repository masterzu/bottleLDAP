%rebase base title="serveurs LDAP : %s" % name, nav=nav, warn=warn, author=author, version=version

<script type="text/javascript">
<!--
$(function() {

    $('button#issue').click(function(){
        var this_button = $(this);
        var this_span = $(this).next();
        var url = '/api/server/{{name}}';
        //alert('serveur {{name}} with url:'+url);
        this_span.addClass('ui-qutocomplete-loading').text('en recherche ...');


        $.getJSON(url,function(data, textStatus){
            this_span.removeClass('ui-qutocomplete-loading').text('');
            if (textStatus == 'success') { // ajax OK
                if (data['success']) {
                    this_span.text(data['message']);
                } else {
                    show_warning(data['message']);
                }
                
            } else {
                show_warning('NOOOOO !!! ajax error');
            }
        });
    }); 

});
// -->
</script>

<div class="box shadow">
<h1>serveur <span id="server">{{name}}</span></h1>
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
            <span name="issue">&nbsp;</span>
        </li>
    <ul>
</div><!-- box shadow -->

