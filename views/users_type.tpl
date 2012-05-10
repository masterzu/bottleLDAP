%rebase base title="Utilisateurs", nav=nav, warn=warn, author=author, version=version

%attrs = [ ('givenName', u'prénom'), ('sn', 'nom de famille'), ('cn', "nom d'usage (prénom + nom)"), ('mail', 'email'), ('description', u'description (thème de recherche )')  ]
<script type="text/javascript">
<!--
// script to handle add user form
$(function() { 
    
    // autocomplete functions to handle multivalue ; separated fields
    function autocomplete_split (val){
        return val.split(/\s*;\s*/);
    };
    function autocomplete_last(term) {
        return autocomplete_split(term).pop();
    };

    // add user slide
    $('button#add').click(function () {
        $('#form').slideToggle('slow');
    });
    // capitalize the given name && update field cn
    $("input[name='givenName']").change(function(){
        var val = $(this).val().capitalize();
        $(this).val(val);
        $("input[name='cn']").val($("input[name='givenName']").val()+' '+$("input[name='sn']").val());
        var pre = $("input[name='givenName']").val().toLowerCase();
        var nom = $("input[name='sn']").val().toLowerCase();
        if (pre && nom) $("input[name='mail']").val(pre+'.'+nom+'@upmc.fr');
    });
    // upper the familly name (sn) && update field cn
    $("input[name='sn']").change(function(){
        var val = $(this).val().toUpperCase();
        $(this).val(val);
        $("input[name='cn']").val($("input[name='givenName']").val()+' '+$("input[name='sn']").val());
        var pre = $("input[name='givenName']").val().toLowerCase();
        var nom = $("input[name='sn']").val().toLowerCase();
        if (pre && nom) $("input[name='mail']").val(pre+'.'+nom+'@upmc.fr');
    });
    // email validation
    // http://www.designchemical.com/blog/index.php/jquery/email-validation-using-jquery/
    $("input[name='mail']").change(function() {
        var emailre = /^([\w-\.]+@([\w-]+\.)+[\w-]{2,4})?$/;
        var email = $(this).val();
        if (!emailre.test(email)) {
            alert('email non valide');
            $(this).focus();
        } else {
            //alert('email OK');
            $(this).blur();
        }
    });
    // populate select #select-group
    $.getJSON('/api/groups',function(data, textStatus){
        if (textStatus == 'success') { // ajax OK
            $.each(data['groups'], function(){
                //alert(data['groups'][g]['cn']);
                //alert(this.cn);
                $("#select-group").append('<option value="' + this.dn + '">' + this.description + '</option>');
            });
        } else { // ajax error
            show_warning('AJAX: error: GET '+url);
        }
    });
    // user type change
    $("#select-usertype").change(function(){
        var val = $(this).val();
        if (val == 'p') {
            $("#tr-group").show();
            $("#tr-manager").hide();
        } else if (val == 'd' || val == 't') {
            $("#tr-group").hide();
            $("#tr-manager").show();
            //alert('Not Yet Implemented');
        }
    });


    // directeur
    $("input[name='manager']").autocomplete({
        source: function (request, response) {
            $.getJSON( '/api/autocomplete_manager', 
                { term: autocomplete_last(request.term) }, 
                response );
        }, 
        search: function () {
            var term = autocomplete_last(this.value);
            if (term.length < 2) {
                return false;
            }
        }, 
        select: function(e,ui) {
           // alert('SELECT item.id='+ui.item.id+'; item.value='+ui.item.value);
           var terms = autocomplete_split(this.value);
           // remove the last
           terms.pop();
           // add the new selected item
           terms.push(ui.item.value);
           // add an empty item to have the last ;
           terms.push('');
           this.value = terms.join(' ; ');
           // update width handled by autoGrowInput (blur event)
           this.blur(); this.focus();
           return false;
        }
    }).autoGrowInput(
        {maxWidth: 600, comfortZone: 10}
    );

    // bouton ajouter
    $("button[name='ajouter']").click(function(){
        var givenName = $("input[name='givenName']").val();
        var sn = $("input[name='sn']").val();
        var cn = $("input[name='cn']").val();
        var mail = $("input[name='mail']").val();
        var description = $("input[name='description']").val();
        var usertype = $("#select-usertype").val();
        var uid = $("#tr-uid input").val();

        if (! givenName) {
            alert('Mettre un prénom');
            $("input[name='givenName']").focus();
            return;
        } else if (!sn) {
            alert('Mettre un nom de famille');
            $("input[name='sn']").focus();
            return;
        } else if (!cn) {
            alert("Mettre un nom d'usage");
            $("input[name='cn']").focus();
            return;
        } else if (!mail) {
            alert('Mettre un email');
            $("input[name='mail']").focus();
            return;
        } else if (!description) {
            alert('Mettre une description');
            $("input[name='description']").focus();
            return;
        };
        //alert(givenName+'|'+sn+'|'+cn+'|'+mail+'|'+description+'|'+usertype);

        var data = {};
        data['givenName'] = givenName;
        data['sn'] = sn;
        data['cn'] = cn;
        data['mail'] = mail;
        data['description'] = description;
        data['usertype'] = usertype;
        if (uid) data['uid'] = uid;
        

        if (usertype == 'p') {
            var group = $("#select-group").val();
            data['group'] = group;

        } else if (usertype == 'd' || usertype == 't') {
            //alert('Not Yet Implemented');
            var manager = $("input[name='manager']").val();
            data['manager'] = manager;
            if (! manager) {
                alert('Mettre un directeur');
                $("input[name='manager']").focus();
                return;
            }
        }
        
        var url = '/api/useradd';
        //alert('post on '+url+' with: '+data);
        $.post(url,data,function(dataout, textStatus){
            if (textStatus == 'success') { // ajax OK
                //alert('OK JSON='+dataout['uid']);
                if (dataout['success']) { // operation done
                    var uid = dataout['uid'];
                    var userPassword = dataout['userPassword'];
                    alert('Utilisateur crée avec le login:'+uid+' et le mot de passe:'+userPassword);
                    alert('Il reste a créer le compte sur le serveur NFS (olympe)');
                    location.href='/user/'+uid;

                } else { // operation failed
                    var message = dataout['message'];
                    if (message == 'no_free_uid'){
                        $('#tr-uid').show('fast');
                        show_warning('champs uid existe déjà. Choisissez une autre valeur.');
                        $('#tr-uid input').focus();
                    } else {
                        show_warning(dataout['message']);
                    }
                }
            } else { // ajax failed
                show_warning('AJAX: error: POST '+url);
            };
        } ,'json');

    });



    
});
//-->
</script>

<div class="box shadow">
    <h1>{{title}}</h1>

    <button id="add" name="add">ajouter un utilisateur...</button>
    <div id="form" class="box shadow hide">
        <table cellspacing="1" width="100%">
        <tbody>
            <tr>
                <td colspan="2"><hr/><td>
            </tr>
%for id, id_name in attrs:
            <tr>
                <th title="champs LDAP: {{id}}">{{id_name}}</th>
                <!--td style="text-align: right; font-size: smaller;font-family: monospace" title="champs LDAP">({{id}})</td -->
            %if id == 'description':
                <td><input type="text" name="{{id}}" size="50"/></td>
            %else:
                <td><input type="text" name="{{id}}"/></td>
            %end
            </tr>
%end
            <tr id="tr-uid">
                <td style="text-align: center">login (optionnel)</td>
                <td><input type="text" name="uid"/></td>
            </tr>
            <tr>
                <th>type d'utilisateur</th>
                <td>
                    <select name="usertype" id="select-usertype">
                    %for type, name in [('p', 'pernament'), ('d', 'doctorant'), ('t', u'étudiant ou invité')]:
                    <option value="{{type}}">{{name}}</option>
                    %end
                    </select>
                </td>
            </tr>
            <tr id="tr-group">
                <th>équipe</th>
                <td><select name="group" id="select-group"></select></td>
            </tr>
            <tr id="tr-manager" class="hide">
                <th>directeur</th>
                <td>
                    <input type="text" name="manager">
                </td>
            </tr>
            <tr>
                <td colspan="2"><hr/><td>
            </tr>
            <tr>
                <td colspan="2" style="text-align: center"><button name="ajouter">ajouter</button></td>
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


