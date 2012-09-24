%rebase base title="serveur LDAP : %s" % name, nav=nav, warn=warn, author=author, version=version

<script type="text/javascript">
<!--
$(function() {

    $('button#issue').click(function(){
        var this_button = $(this);
        var this_span = $(this).next();
        var url = '/api/server/{{name}}';
        //alert('serveur {{name}} with url:'+url);
        this_span.addClass('ui-autocomplete-loading').text('connecting to {{name}} ......');


        /*
        $.getJSON(url,function(data, textStatus){
            this_span.removeClass('ui-autocomplete-loading').text('');
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
        */
        // test timeout http://stackoverflow.com/questions/3543683/jquery-ajax-timeout-setting
        $.ajax({
            url: url,
            type: "GET",
            dataType: "json",
            timeout: 1500,
            success: function(response) {
                this_span.removeClass('ui-autocomplete-loading').text('');
                if (response['success']) {
                    this_span.text(response['message']);
                } else {
                    show_warning(response['message']);
                }
            },
            error: function(xhr, textStatus, error) {
                this_span.removeClass('ui-autocomplete-loading').text('');
                if (textStatus == "timeout")
                    show_warning('Serveur Timeout ... Réessayez si vous osez :)')
                else 
                    show_warning('Erreur de serveur: '+error+' ('+textStatus+')');
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

