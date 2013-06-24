%rebase base title="Utilisateur : %s" % uid, nav=nav, warn=warn, author=author, version=version

%mandatory_attrs = ['sn','cn','uidNumber','gidNumber', 'homeDirectory']
%if len(users) > 0:
<script type="text/javascript">
<!-- 
$(function() {
    // general {span,input,button}[name=name] function
    // change the text of corresponding tag name 
    function set_fields(name, text) {
        var span_filters = "span[name='" + name + "']"
        var span_filters_hide = "#fields span[name='" + name + "']"
        var input_filters = "input[name='" + name + "']"
        var button_filters = "button[name='" + name + "']"

        if (text) {
            $(span_filters).removeClass('warning').text(text);
            $(input_filters).val(text);
        } else {
            $(span_filters_hide).addClass('warning');
            $(span_filters).text('vide');
            $(input_filters).val('');
        }
        if (name == 'mail') {
            var mailto = 'mailto:'+text;
            $("a[name='mail']").attr('href',mailto).text(text);
        }
    };
  
    // autocomplete functions to handle multivalue ; separated fields
    function autocomplete_split (val){
        return val.split(/\s*;\s*/);
    };
    function autocomplete_last(term) {
        return autocomplete_split(term).pop();
    };

    // #page span#home
    function get_home(button, url, span) {
        span.addClass('ui-autocomplete-loading').html('&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;');

        // do the ajax job with a timeout
        $.ajax({
            url: url,
            type: "GET",
            dataType: "json",
            timeout: 1500,
            success: function(response) {
                span.removeClass('ui-autocomplete-loading').text('');
                if (response['success']) {
                    button.hide();
                    var attrs = new Array('server', 'quota', 'dirdate', 'owner', 'rights');
                    for (var k in attrs) {
                        var key = attrs[k],
                            val = response[key];
                        span.before('<dt>'+key+'</dt>');
                        switch(key) {
                        
                        case 'server':
                            span.before('<dd><a href="/server_nfs/'+val+'">'+val+'</a></dd>');
                            break;

                        case 'quota':
                            var size = val[0],
                                soft = val[1],
                                hard = val[2],
                                grace = val[3],
                                text = '',
                                okcolor = 'green',
                                softcolor = 'orange',
                                hardcolor = 'red',
                                sizecolor, 
                                sizeprec = 0,
                                softprec = 0,
                                hardprec = 0;
                            if (size < soft || ( soft == 0 && hard == 0)) {
                                sizecolor = okcolor;
                            } else { 
                                if (soft <= size && size < hard) {
                                    sizecolor = softcolor;
                                    sizeprec = 2;
                                    softprec = 2;
                                } else {
                                    sizecolor = hardcolor;
                                    sizeprec = 2;
                                    hardprec = 2;
                                }
                            }
                            text = 'size=<span title="'+size+' ko" style="color:'+sizecolor+';">'+kilobytesToSize(size, sizeprec)+'</span>, ';
                            text += 'soft=<span title="'+soft+' ko" style="color:'+softcolor+';">'+kilobytesToSize(soft, softprec)+'</span>, ';
                            text += 'hard=<span title="'+hard+' ko" style="color:'+hardcolor+';">'+kilobytesToSize(hard, hardprec)+'</span>, ';
                            if (grace)
                                text += 'grace='+grace
                            else
                                text += 'grace=<span style="font-style:italic;">N/A</span>';
                            span.before('<dd>'+text+'</dd>');
                            break;

                        default:
                            span.before('<dd><code>'+val+'</code></dd>');
                        }

                    }
                } else {
                    show_warning(response['message'])
                }
            },
            error: function(xhr, textStatus, error) {
                span.removeClass('ui-autocomplete-loading').text('');
                if (textStatus == "timeout")
                    show_warning('Serveur Timeout ... Réessayez si vous osez :)')
                else 
                    show_warning('Erreur de serveur: '+error+' ('+textStatus+')');
            }
        });
    };
    $('button[name=home]','#page').click(function(){
        get_home($(this), '/api/user/{{uid}}/home', $('span[name=home]', '#page'));

    });


    //  general #fields span
    $('#fields span').click(function () {
        $(this).hide().next().show().next().show();
        $(this).next().focus();
    });
    // span[name=manager]
    $("span[name='manager']").click(function () {
        $(this).hide().next().show().next().next().show();
        $(this).next().focus();
    });

    // #fields input keypress=<enter> 
    // + empty value >> remove attr
    $('table#fields input').keypress(function(e) {
        if ((e.which == 13)) {
            var attr = $(this).attr('name');
            var this_span = $(this).prev('span');
            var this_input = $(this);
            var this_button = $(this).next('button');
            var oldval = this_span.val();
            var newval = $(this).val();

            if (newval == oldval){
                this_span.show();
                this_input.hide();
                this_button.hide();
                return false;
            };
            /*
            Only handle the first value
            var vals = new Array();
            $("table#fields input[id*='"+attr+"']").each(function(){
                vals.push($(this).val());
            });
            alert('vals='+vals);
            */
            var url = '/api/user/{{uid}}/attr/' + attr;

            // set the new value with ajax
            $.post(url,{'newval': newval},function(data, textStatus){
                if (textStatus == 'success') { // ajax OK
                    //alert('OK JSON='+data[attr]);
                    if (! data['success']) { // operation failed
                        show_warning(data['message']);
                        set_fields(attr, this_span.val());
                    } else { // operation done
                        newval = data[attr];
                        set_fields(attr, newval);
                        this_span.show();
                        this_input.hide();
                        this_button.hide();
                    }
                } else { // ajax failed
                    show_warning('AJAX: error: POST '+url);
                    set_fields(attr, this_span.val());
                };
            } ,'json');
        };
    /*
    }).change(function(){
        // DEBUG with #warning
        $('#warning').text($(this).attr('id')+':'+$(this).val());
    */
    });

    // #fields button[reset].click()
    $("#fields button[value=reset]").click(function(){
        var attr = $(this).attr('name');
        var this_span = $(this).prev().prev();
        var this_input = $(this).prev();
        var this_button = $(this);
        var url = '/api/user/{{uid}}/attr/' + attr;

        // load in span
        $.getJSON(url,function(data, textStatus){
            if (textStatus == 'success') { // ajax OK
                //alert('OK JSON='+data[attr]);
                set_fields(attr, data[attr]);
                this_span.show();
                this_input.hide();
                this_button.hide();

            } else { //ajax error
                show_warning('AJAX: error: GET '+url);
                set_fields(attr, this_span.val());
            };

        });
    });

    $("input[name='manager']").autocomplete({
        source: function (request, response) {
            $.getJSON( '/api/autocomplete_manager', 
                { term: autocomplete_last(request.term) }, 
                response);
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
    ).keypress(function(e){
        if ((e.which == 13)) {
            var this_span = $(this).prev();
            var this_input = $(this);
            var this_button = $(this).next().next();
            var oldval = this_span.val();
            var newval = $(this).val();

            if (newval == oldval) {
                this_span.show();
                this_input.hide();
                this_button.hide();
                return false;
            };
            //alert('newval='+newval);
            var attr = 'manager';
            var url = '/api/user/{{uid}}/attr/manager';

            // set the new value with ajax
            $.post(url,{'newval': newval},function(data, textStatus){
                if (textStatus == 'success') { // ajax OK
                    //alert('OK JSON');
                    //for ( var v in data) { alert('data['+v+']='+data[v]);};
                    if (data['success']) { // operation done
                        this_span.show().text(data['cn']);
                        this_input.hide().val(data['dn']);
                        this_button.hide();
                    } else { // operation failed
                        show_warning(data['message']);
                        set_fields(attr, this_span.val());
                        //$("button[name=manager]").click();
                    }
                } else { // ajax failed
                    show_warning('AJAX: error: POST '+url);
                    set_fields(attr, this_span.val());
                };
            } ,'json');
        };
            
    });

    // button[name=manager].click() reset
    $("button[name=manager]").click(function(){
        var attr = 'manager';
        var this_span = $(this).prev().prev().prev();
        var this_input = $(this).prev().prev();
        var this_button = $(this);
        var url = '/api/user/{{uid}}/attr/manager';

        // load in span
        $.getJSON(url,function(data, textStatus){
            if (textStatus == 'success') { // ajax OK
                //alert('OK JSON='+data[attr]);
                
                this_span.show().text(data['cn']);
                this_input.hide().val(data['dn']);
                this_button.hide();

            } else { //ajax error
                show_warning('AJAX: error: GET '+url);
                set_fields(attr, this_span.val());
            };

        });
    });

    // #fields button#delete
    $('#delete').click(function(){
        $(this).hide();
        $('#dialog').show();
        alert("ATTENTION : Cette opération va supprimer toutes les informations LDAP et NFS du compte.\nCette action peut bloquer la reactivité du serveur ... c'est un comportement attendu.");
    });
    
    // #fields button#delete_no
    $('#delete_no').click(function(){
        $('#dialog').hide();
        $('#delete').show();
    });
    
    // #fields button#delete_yes
    $('#delete_yes').click(function(){
        $('#dialog').hide();
        $('#delete').show();
        var url = '/api/userdel';
        $.post(url,{'uid': '{{uid}}'},function(data, textStatus){
            if (textStatus == 'success') { // ajax OK
                //alert('OK JSON='+data[attr]);
                if (data['success']) { // operation done
                    alert('Utilisateur "{{uid}}" supprimé');
                    location.href='/';
                } else { // operation failed
                    show_warning(data['message']);
                }
            } else { // ajax failed
                show_warning('AJAX: error: POST '+url);
                set_fields(attr, this_span.val());
            };
        } ,'json');

    });

    // click on load
    log_on_click($('#addlogd'), '/api/log/user/{{uid}}', $('#logs-texts'));
});
// -->
</script>

<!--div id="onglets"-->
<div id="onglets">
    <ul class="nav nav-tabs">
        <li class="active"><a href="#page" class="actif nav">fiche</a></li>
        <li><a href="#fiche" class="nav">édition</a></li>
        <li><a href="#logs" class="nav">logs</a></li>
    </ul>

    <div id="page" class="onglet box shadow">
    %dn = users[0][0]
    %u =  users[0][1]
    <!-- ONLY PRINT the first user -->
        <h1><span name="cn" title="cn">{{u['cn'][0]}}</span></h1>
        <div style="float: left">
        <dl>
            <dt title="givenName">Prénom</dt>
        %if 'givenName' in u:
            <dd><span name="givenName">{{u['givenName'][0]}}</span></dd>
        %else:
            <dd class="warning">pas de prénom définit !</dd>
        %end
            <dt title="sn">Nom de famille</dt>
            <dd><span name="sn">{{u['sn'][0]}}</span></dd>
            <dt title="mail">email</dt>
        %if 'mail' in u:
            <dd><a name="mail" class="email" href="mailto:{{u['mail'][0]}}">{{u['mail'][0]}}</a></dd>
        %else:
            <dd class="warning">pas d'email définit !</dd>
        %end

            <dt title="description">description</dt>
        %if 'description' in u:
            <dd><span name="description">{{u['description'][0]}}</span></dd>
        %else:
            <dd class="warning">pas définit !</dd>
        %end

            
        %if len(teams) > 1:
            <dt>équipes</dt>
        %else:
            %if len(teams) == 1:
            <dt>équipe</dt>
            %end
        %end
        %for tdn, t in teams:
            <dd><a href="/group/{{t['cn'][0]}}">{{t['description'][0]}}</a> (<code>{{t['cn'][0]}}</code>)</dd>
        %end
        </dl>
        </div>

        <div style="float: right">
        <dl>
            <dt title="uid">login</dt>
            <dd><code>{{uid}}</code></dd>

            <dt title="home">$HOME</dt>
            <dd><code>{{u['homeDirectory'][0]}}</code></dd>
            <button name="home">+ infos</button>
            <span name="home"></span>

        </dl>
        </div>

        <div style="clear: both">
        <dl>
        %if len(managers) > 1:
            <dt title="manager">directeurs</dt>
        %else:
            %if len(managers) == 1:
            <dt title="manager">directeur</dt>
            %end
        %end
        %for mandn, man in managers:
            <dd><a href="/user/{{man['uid'][0]}}">{{man['cn'][0]}}</a></dd>
        %end

        %if len(phds) > 1:
            <dt>{{len(phds)}} doctorants</dt>
        %else:
            %if len(phds) == 1:
            <dt>doctorant</dt>
            %end
        %end
        %for stu in phds:
            %if 'description' in stu:
                %desc = stu['description'][0]
            %else:
                %desc = ''
            %end
            %if 'mail' in stu:
                %email = '(' + stu['mail'][0] + ')'
                %emailink = 'mailto:' + email
            %else:
                %email = "(pas d'email)"
                %emailink = ''
            %end
            <dd><a href="/user/{{stu['uid'][0]}}">{{stu['cn'][0]}}</a> {{desc}} <a href="{{emailink}}" class="email">{{email}}</a></dd>
        %end

        %if len(students) > 1:
            <dt>{{len(students)}} étudiants</dt>
        %else:
            %if len(students) == 1:
            <dt>étudiant</dt>
            %end
        %end
        %for stu in students:
            %if 'description' in stu:
                %desc = stu['description'][0]
            %else:
                %desc = ''
            %end
            %if 'mail' in stu:
                %email = '(' + stu['mail'][0] + ')'
                %emailink = 'mailto:' + email
            %else:
                %email = "(pas d'email)"
                %emailink = ''
            %end
            <dd><a href="/user/{{stu['uid'][0]}}">{{stu['cn'][0]}}</a> {{desc}} <a href="{{emailink}}" class="email">{{email}}</a></dd>
        %end

        %if len(assistants) > 1:
            <dt>{{len(assistants)}} assistants</dt>
        %else:
            %if len(assistants) == 1:
            <dt>assistant</dt>
            %end
        %end
        %for stu in assistants:
            %if 'description' in stu:
                %desc = stu['description'][0]
            %else:
                %desc = ''
            %end
            %if 'mail' in stu:
                %email = '(' + stu['mail'][0] + ')'
                %emailink = 'mailto:' + email
            %else:
                %email = "(pas d'email)"
                %emailink = ''
            %end
            <dd><a href="/user/{{stu['uid'][0]}}">{{stu['cn'][0]}}</a> {{desc}} <a href="{{emailink}}" class="email">{{email}}</a></dd>
        %end

        </dl>
        </div>
    </div><!-- onglet page -->

    <div id="fiche" class="onglet box shadow">
        <h1>fiche LDAP : {{u['cn'][0]}}</h1>
        <button id="delete">supprimer la fiche</button>
        <div id="dialog" class="hide">Ètes vous sure ? <button id="delete_yes">oui</button><button id="delete_no">non</button></div>
        <h2>champs fixes</h2>
        <table>
            <tr>
                <th>dn</th>
                <td>{{dn}}</td>
            </tr>
            <tr>
                <th>uid</th>
                <td id="uid">{{uid}}</td>
            </tr>
        </table>

        <h2>champs modifiables</h2>
        <table id="fields">
        %for f in ['givenName','sn','cn','description','mail','uidNumber','gidNumber','homeDirectory','loginShell','userPassword']:
            %if f in u:
                %span_val = u[f][0]
                %input_val = u[f][0]
                %cls = 'cliquable'
            %else:
                %span_val = 'vide'
                %input_val = ''
                %cls = 'warning cliquable'
            %end
            <tr>
                <th>
                    %if f in mandatory_attrs: 
                    <span title="champs obligatoire LDAP" style="cursor:help; color:red;">{{f}}*</span>
                    %else:
                    {{f}}
                    %end
                </th>
                <td>
                    <span   name="{{f}}" class="{{cls}}">{{span_val}}</span>
                    <input  name="{{f}}" type="text"   value="{{input_val}}" style="display:none;">
                    <button name="{{f}}" type="button" value="reset"         style="display:none;">reset</button>
                </td>
            </tr>
        %end
        </table>
        <table id="fields_special">
        <h2>champs spéciaux</h2>
            %if len(managers) > 0:
                %managers_cn = ', '.join([man['cn'][0] for mandn, man in managers ])
                %cls = 'cliquable'
                %managers_dn = ' ; '.join([mandn for mandn, man in managers ])
                %managers_dn += ' ; '
            %else:
                %managers_cn = 'vide' 
                %cls = 'cliquable warning'
                %managers_dn = ''
            %end
            <tr>
                <th name="manager">manager</th>
                <td> 
                    <span     name="manager" class="{{cls}}">{{managers_cn}}</span>
                    <input    name="manager" type="text"   value="{{managers_dn}}" style="display:none">
                    <button   name="manager" type="button" value="reset"           style="display:none">reset</button>
                </td>
            </tr>
        </table>
        
        %if len(teams) > 0 or len(phds) > 0 or len(students) > 0: 
        <h2>champs externes</h2>
        <table>
            %for tdn, t in teams:
            <tr>
                <th>
                    équipe
                </th>
                <td>
                    <a href="/group/{{t['cn'][0]}}">{{t['description'][0]}}</a>
                </td>
            </tr>
            %end
            %for phd in phds:
            <tr>
                <th>doctorant</th> 
                <td>{{phd['cn'][0]}}</td>
            </tr>
            %end
            %for stu in students:
            <tr>
                <th>étudiant</th> 
                <td>{{stu['cn'][0]}}</td>
            </tr>
            %end
        </table>
        %end

    </div><!-- onglet fiche -->

    <div id="logs" class="onglet box shadow">
        <h1 id="heading">fiche LOGS : {{u['cn'][0]}}</h1>
        <div>Liste anti-chronologique des logs.</div>
        <button id="addlogd">afficher a jour les logs</button>
        <div id="logs-texts"> </div>
        
    </div><!-- onglet logs -->

</div><!-- onglets -->
%else:
<div>Erreur : Il n'existe pas de compte <code>{{uid}}</code>
</div>
%end

