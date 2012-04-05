%rebase base title="Utilisateurs", nav=nav, warn=warn, author=author, version=version

<div class="box shadow">
<h1>{{title}}</h1>

%l = len(users)
<p> Il y a {{l}} {{title}} dans l'annuaire.  </p>


<script type = "text/javascript">
$(document).ready(function() 
    { 
        $("#users").tablesorter({
            // sort on first column
            sortList: [[0,0]]
        }); 
    } 
);
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


