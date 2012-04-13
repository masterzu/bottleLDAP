%rebase base title="Utilisateurs : %s" % uid, nav=nav, warn=warn, author=author, version=version

%mandatory_attrs = ['sn','cn','uidNumber','gidNumber', 'homeDirectory']
%if len(users) > 0:
<div id="onglets">
    <ul>
        <li><a href="#page" class="actif nav">fiche</a></li>
        <li><a href="#fiche" class="nav">édition</a></li>
    </ul>

<script type="text/javascript">
<!-- 
$(function() {
    // #fields
    var css_show_inline = { 'display': 'inline'};
    var css_show_block = { 'display': 'block'};
    var css_hide = { 'display': 'none'};

    function set_fields(name, text) {
    // set span.text; input.value; show span; hide input and button
        var span_filters = "span[name='" + name + "']"
        var span_filters_hide = "#fileds span[name='" + name + "']"
        var input_filters = "input[name='" + name + "']"
        var button_filters = "button[name='" + name + "']"

        $(span_filters).css(css_show_inline);
        if (text) {
            $(span_filters).removeClass('warning').text(text);
            $(input_filters).val(text);
        } else {
            $(span_filters_hide).addClass('warning');
            $(span_filters).text('vide');
            $(input_filters).val('');
        }
        $(span_filters_hide).css(css_hide);
        $(button_filters).css(css_hide);
        if (name == 'mail') {
            var mailto = 'mailto:'+text;
            $("a[name='mail']").attr('href',mailto).text(text);
        }
    };
    
    // #fields span.click()
    $('table#fields span').click(function () {
        $(this).css(css_hide).next().css(css_show_inline).next().css(css_show_inline);
    });

    // #fields input keypress=<enter> 
    $('table#fields input').keypress(function(e) {
        if ((e.which == 13) && $(this).val() != '') {
            var attr = $(this).attr('name');
            var this_span = $(this).prev('span');
            var this_input = $(this);
            var this_button = $(this).next('button');
            var oldval = this_span.val();
            var newval = $(this).val();
            /*
            Only handle the first value
            var vals = new Array();
            $("table#fields input[id*='"+attr+"']").each(function(){
                vals.push($(this).val());
            });
            alert('vals='+vals);
            */
            var url = '/api/user/' + $('#uid').text() + '/attr/' + attr;

            // post ajax
            $.post(url,{'attr': attr, 'newval': newval},function(data, textStatus){
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
    $("table#fields button[value=reset]").click(function(){
        var attr = $(this).attr('name');
        var this_span = $(this).prev().prev();
        var this_input = $(this).prev();
        var this_button = $(this);
        var url = '/api/user/' + $('#uid').text() + '/attr/' + attr;

        // load in span
        $.getJSON(url,function(data, textStatus){
            if (textStatus == 'success') { // ajax OK
                //alert('OK JSON='+data[attr]);
                var text = data[attr];
                set_fields(attr, text);
                this_span.show();
                this_input.hide();
                this_button.hide();

            } else { //ajax error
                show_warning('AJAX: error: GET '+url);
                var text = this_span.val();
                set_fields(attr, text);
            };

        });
    });

    // #fields button#delete
    $('#delete').click(function(){
        $(this).hide();
        $('#dialog').show();
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
        var uid = $('#uid').text();
        var url = '/api/userdel';
        $.post(url,{'uid': uid},function(data, textStatus){
            if (textStatus == 'success') { // ajax OK
                //alert('OK JSON='+data[attr]);
                if (data['success']) { // operation done
                    alert('Utilisateur '+uid+' supprimé');
                    alert('Il reste a supprimer le compte sur le serveur NFS (olympe)');
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
})
// -->
</script>

    <div id="page" class="onglet box shadow">
    %dn = users[0][0]
    %u =  users[0][1]
    <!-- ONLY PRINT the first user -->
        <h1><span name="cn" title="cn">{{u['cn'][0]}}</span></h1>
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

        %if 'description' in u:
            <dt title="description">description</dt>
            <dd><span name="description">{{u['description'][0]}}</span></dd>
        %end

        %if len(teams) > 1:
            <dt>équipes</dt>
        %else:
            %if len(teams) == 1:
            <dt>équipe</dt>
            %end
        %end
        %for tdn, t in teams:
            <dd><a href="/group/{{t['cn'][0]}}">{{t['description'][0]}}</a></dd>
        %end

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
        %for phd in phds:
            %if 'description' in phd:
                %desc = phd['description'][0]
            %else:
                %desc = ''
            %end
            <dd><a href="/user/{{phd['uid'][0]}}">{{phd['cn'][0]}}</a> {{desc}}</dd>
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
            <dd><a href="/user/{{stu['uid'][0]}}">{{stu['cn'][0]}}</a> {{desc}}</dd>
        %end
        </dl>
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
        %for f in ['manager']:
            %if f in u:
                %for u_i in u[f]:
            <tr>
                <th>{{f}}</th>
                <td>
                    {{u_i}}
                </td>
            </tr>
                %end
            %end
        %end
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

        <h2>champs externes</h2>
        <table>
        %for tdn, t in teams:
            <tr>
                <th>
                    équipe
                </th>
                <td>
                    {{t['description'][0]}}
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

    </div><!-- onglet fiche -->

</div><!-- onglets -->
%end

