%rebase base title="Utilisateurs", nav=nav, warn=warn, author=author, version=version
%# 
%# Vars: nfs_servers, users
%#
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
    $("input[name='givenName']").blur(function(){
        var val = $(this).val().capitalize();
        $(this).val(val);
        $("input[name='cn']").val($("input[name='givenName']").val()+' '+$("input[name='sn']").val());
        var pre = $("input[name='givenName']").val().toLowerCase();
        var nom = $("input[name='sn']").val().toLowerCase();
        var login = pre + '.' + nom
        var mail = $("input[name='mail']").val();
        var heywoodlogin = $("#heywoodlogin").val();
        if (pre && nom && !mail) $("input[name='mail']").val(login.login() + '@upmc.fr');
        if (pre && nom && !heywoodlogin) $("#heywoodlogin").val(login.login());
    });
    // upper the familly name (sn) && update field cn
    $("input[name='sn']").blur(function(){
        var val = $(this).val().toUpperCase();
        $(this).val(val);
        $("input[name='cn']").val($("input[name='givenName']").val()+' '+$("input[name='sn']").val());
        var pre = $("input[name='givenName']").val().toLowerCase();
        var nom = $("input[name='sn']").val().toLowerCase();
        var login = pre + '.' + nom
        var mail = $("input[name='mail']").val();
        var heywoodlogin = $("#heywoodlogin").val();
        if (pre && nom && !mail) $("input[name='mail']").val(login.login() + '@upmc.fr');
        if (pre && nom && !heywoodlogin) $("#heywoodlogin").val(login.login());
    });
    // email validation
    // http://www.designchemical.com/blog/index.php/jquery/email-validation-using-jquery/
    $("input[name='mail']").change(function() {
        var emailre = /^([\w-\.]+@([\w-]+\.)+[\w-]{2,})?$/;
        var email = $(this).val();
        if (!emailre.test(email)) {
            alert('email non valide');
            $(this).focus();
        } else {
            //alert('email OK');
            $(this).blur();
        }
        });

    // checkbox mail
    $("input#cbcreateemail").change(function(){
        var checked = $(this).prop('checked');
        // alert(checked); 
        if(checked){
            $("#heywoodlogin").prop({disabled: false});
            $("#email").prop({disabled: true});
        } else {
            $("#email").prop({disabled: false});
            $("#heywoodlogin").prop({disabled: true});
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
        var heywoodlogin = $("#heywoodlogin").val();
        var cbcreateemail = $('#cbcreateemail').prop('checked');
        var description = $("input[name='description']").val();
        var usertype = $("#select-usertype").val();
        var hostname = $("#select-hostname").val();
        var uid = $("#tr-uid input").val();

        function getmail() {
            var cb = cbcreateemail;
            var e1 = heywoodlogin + '@dalembert.upmc.fr';
            var e2 = mail;
            if (cb) 
                return e1
            else
                return e2
        };

        if (! givenName) {
            alert('Mettre un prénom');
            $("input[name='givenName']").focus();
            return;
        } 
        if (!sn) {
            alert('Mettre un nom de famille');
            $("input[name='sn']").focus();
            return;
        } 
        if (!cn) {
            alert("Mettre un nom d'usage");
            $("input[name='cn']").focus();
            return;
        } 
        if (!cbcreateemail){
            if (!mail) {
                alert('Mettre un email existant');
                $("input[name='mail']").focus();
                return;
            }
        } else {
            if (!heywoodlogin) {
                alert('Mettre un compte a créer');
                $("#heywoodlogin").focus();
                return;
            }
        } 
        if (!description) {
            alert('Mettre une description');
            $("input[name='description']").focus();
            return;
        };
        //alert(givenName+'|'+sn+'|'+cn+'|'+mail+'|'+description+'|'+usertype);

        // from here all datas are valid
        var data = {};
        data['givenName'] = givenName;
        data['sn'] = sn;
        data['cn'] = cn;
        data['mail'] = getmail();
        data['description'] = description;
        data['usertype'] = usertype;
        data['hostname'] = hostname;
        if (uid) data['uid'] = uid;
        if (cbcreateemail) {
            data['createemail'] = 1;
            data['createemaillogin'] = heywoodlogin;
        }

        if (usertype == 'p') {
            var group = $("#select-group").val();
            data['group'] = group;

        } else if (usertype == 'd' || usertype == 't') {
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
                    var mess = dataout['message'];
                    var message = 'Utilisateur crée avec le login: '+uid+"\net le mot de passe: "+userPassword;
                    if (mess) message += "\n\n"+mess;
                    alert(message);
                    location.href='/user/'+uid;

                } else { // operation failed
                    var message = dataout['message'];
                    if (message == 'user_exists'){
                        // NEEDED? $('#tr-uid').show('fast');
                        show_warning('champs login existe déjà. Choisissez une autre valeur.');
                        $('#tr-uid input').focus();
                    } else {
                        show_warning(message);
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

    <p><button id="add" name="add" class="btn">ajouter un utilisateur...</button></p>
    <div id="form" class="box shadow hide">
        <h3>Nouvel Utilisateur</h3>
        <dl class="dl-horizontal">
        %for id, id_name in attrs:
            %if id == 'mail':
            <dt class="help" title="champs LDAP: {{id}}">{{id_name}} existant &hellip;</dt>
            <dd>
                <input id="email" type="text" name="{{id}}" placeholder="email@whatever.com"/><br/>
            </dd>
            <dt>&hellip; ou
            </dt>
            <dd>
                <label class="checkbox">
                    créer un compte sur <em>heywood</em>
                    <input id="cbcreateemail" type="checkbox" value=""> 
                </label>
                <span class="input-append">
                    <input id="heywoodlogin" type="text" placeholder="john.doe" disabled>
                    <span class="add-on">@dalembert.upmc.fr</span>
                </span>
            </dd>
            %else:
            <dt class="help" title="champs LDAP: {{id}}">{{id_name}}</dt>
            <dd><input type="text" name="{{id}}"/></dd>
            %end
        %end
            <div id="tr-uid">
                <dt style="text-align: center">login (optionnel)</dt>
                <dd><input type="text" name="uid"/></dd>
            </div>
            <dt>type d'utilisateur</dt>
            <dd>
                <select name="usertype" id="select-usertype">
                %for type, name in [('p', 'pernament'), ('d', 'doctorant'), ('t', u'étudiant ou invité')]:
                    <option value="{{type}}">{{name}}</option>
                %end
                </select>
            </dd>
            <div id="tr-group">
                <dt>équipe</dt>
                <dd><select name="group" id="select-group"></select></dd>
            </div>
            <div id="tr-manager" class="hide">
                <dt>directeur</dt>
                <dd><input type="text" name="manager"></dd>
            </div>
            <dt>serveur NFS</dt>
            <dd>
                <select name="hostname" id="select-hostname">
                %for nfs in nfs_servers: 
                <option value="{{nfs}}"
                    %if nfs == 'poisson':
                        selected="selected"
                    %end
                >{{nfs}}</option>
                %end
                </select>
            </dd>
            <dd><button name="ajouter" class="btn btn-small">ajouter</button></dd>
        </dl>

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

<table class="tablesorter table table-hover table-condensed" id="users">
    <thead>
        <tr>
            <th title="cn">Nom d'usage</th>
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
                %if 'mail' in u:
                <a class="email" href="mailto:{{u['mail'][0]}}">{{u['mail'][0]}}</a>
                %else:
                <span class="warning">email non définit</span>
                %end
            </td>
            <td><code>{{u['uid'][0]}}</code></td> 

        </tr>
        %end
    </tbody>
    <tfoot>
        <tr>
            <th title="cn">Nom d'usage</th>
            <th title="mail">email</th>
            <th title="uid">login</th>
        </tr>
    </tfoot>
</table>
</div><!-- box shadow -->

<!-- :vim:ft=html: -->
