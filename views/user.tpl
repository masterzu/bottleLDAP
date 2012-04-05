%rebase base title="Utilisateurs : %s" % uid, nav=nav, warn=warn, author=author, version=version

%mandatory_attrs = ['sn','cn','uidNumber','gidNumber', 'homeDirectory']
%if len(users) > 0:
<div id="onglets">
    <ul>
        <li><a href="#page" class="actif nav">fiche</a></li>
        <li><a href="#fiche" class="nav">édition</a></li>
    </ul>

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
        %for f in ['cn','givenName','sn','description','mail','uidNumber','gidNumber','homeDirectory','loginShell']:
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

