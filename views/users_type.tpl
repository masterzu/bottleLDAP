%rebase base title="Utilisateurs", nav=nav, warn=warn, author=author, version=version

%attrs = [ ('givenName', u'prénom'), ('sn', 'nom de famille'), ('cn', "nom d'usage"), ('mail', 'email'), ('description', 'description')  ]
<script type="text/javascript">
// script to handle add user form
$(function() { 
    
    $('#form').hide();
    $('button#add').click(function () {
        $('#form').slideToggle('slow');
    });
    $("input[name='givenName']").change(function(){
        var val = $(this).val().capitalize();
        $(this).val(val);
        $("input[name='cn']").val($("input[name='givenName']").val()+' '+$("input[name='sn']").val());
    });
    $("input[name='sn']").change(function(){
        var val = $(this).val().toUpperCase();
        $(this).val(val);
        $("input[name='cn']").val($("input[name='givenName']").val()+' '+$("input[name='sn']").val());
    });


    
});
</script>

<div class="box shadow">
    <h1>{{title}}</h1>

    <button id="add" name="ajouter un {{title}}...">ajouter un {{title}}...</button>
    <div id="form" class="box shadow">
        <table cellspacing="1">
        <tbody>
%for id, id_name in attrs:
            <tr>
                <th>{{id_name}}</th>
                <td style="text-align: right; font-size: smaller;font-family: monospace">({{id}})</td>
                <td><input type="text" name="{{id}}"/></td>
            </tr>
%end
            <tr>
                <td></td>
                <td colspan="2" style="text-align: right"><button name="ajouter">ajouter</button></td>
            </tr>
        </tbody>
        </table>

    </div><!-- form -->


    %l = len(users)
    <p> Il y a {{l}} {{title}} dans l'annuaire.  </p>


<script type="text/javascript">
// script to sort #users table
$(function() { 
    $("#users").tablesorter({
        // sort on first column
        sortList: [[0,0]]
    }); 
});
</script>

<table class="tablesorter" id="users" cellspacing="1">
<thead>
    <tr>
        <th title="cn">Nom d'usage</th>
        <th title="givenName">prénom</th>
        <th title="sn">Nom de famille</th>
        <th title="mail">email</th>
        <th title="uid">login</th>
    </tr>
</thead>
<tbody>
%for dn, u in users:
    <tr>
        <td> 
            <a href="/user/{{u['uid'][0]}}" title="{{dn}}">{{u['cn'][0]}}</a>
        </td> 

        <td>
        %if 'givenName' in u:
            {{u['givenName'][0]}}
        %else:
            <span class="warning">prénom non définit</span>
        %end
        </td>
        <td> 
            {{u['sn'][0]}}
        </td> 
        <td>
        %if 'mail' in u:
            <a class="email" href="mailto:{{u['mail'][0]}}">{{u['mail'][0]}}</a>
        %else:
            <span class="warning">email non définit</span>
        %end
        </td>
        <td> {{u['uid'][0]}} </td> 

    </tr>
%end
</tbody>
<tfoot>
    <tr>
        <th title="cn">Nom d'usage</th>
        <th title="givenName">prénom</th>
        <th title="sn">Nom de famille</th>
        <th title="mail">email</th>
        <th title="uid">login</th>
    </tr>
</tfoot>
</table>
</div><!-- box shadow -->


