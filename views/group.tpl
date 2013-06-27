%rebase base title="Équipes : %s" % cn , nav=nav, warn=warn, author=author, version=version


<script type="text/javascript">
<!-- 
$(function() {
    // click on load
        log_on_click($('#addlogd'), '/api/log/group/{{cn}}', $('#logs-texts'));

        $('.toggle').click(function(){
            var item = $(this).next('.toggle-item');
            if (item.css('display') == 'none') {
                item.show('fast');
                $(this).text('-').attr('title', 'fermer');
            } else {
                item.hide('fast');
                $(this).text('+').attr('title', 'ouvrir');
            };

            });
        $('.toggle-all').click(function(){
            if ($(this).text() == 'tout ouvrir') {
                $(this).text('tout fermer');
                $('.toggle-item').show();
            } else {
                $(this).text('tout ouvrir');
                $('.toggle-item').hide();
            };
            $(this).focus();
            });

    
});
// -->
</script>

<div id="onglets">
    <ul class="nav nav-tabs">
        <li><a href="#page" class="nav">fiche</a></li>
        <!-- <li><a href="#fiche" class="nav">édition</a></li> -->
        <li><a href="#logs" class="nav">logs</a></li>
    </ul>

    <div id="page" class="onglet box shadow">
        <h1>{{desc}}</h1>
        <dl class="dl-horizontal">
            %if len(members) == 0:
            <dt>pas de pernament</dt>
            %elif len(members) == 1:
            <dt>1 pernament(e)</dt>
            %else:
            <dt>{{len(members)}} pernament(e)s</dt>
            %end

            <dd>
            %lm = []
            %for u in members:
                %s = '<a href="/user/%s">%s</a>' % (u['uid'], u['cn'])
                %if 'desc' in u and u['desc']:
                    %s+= '&nbsp;<small title="description">(%s)</small>' % u['desc']
                %end
                %lm.append(s)    
            %end
            %sm = ' &nbsp;&bull;&nbsp; '.join(lm)
            {{!sm}}
            </dd>
        </dl>
        <dl class="dl-horizontal">
        %if len(phds) == 0:
            <dt>pas de doctorant</dt>
        %elif len(phds) == 1:
            <dt>1 doctorant(e)</dt>
        %else:
            <dt>{{len(phds)}} doctorant(e)s</dt>
        %end
            <dd>
            %lp = []
            %for u in phds:
                %lh = []
                %s = '<a href="/user/%s">%s</a>' % (u['uid'], u['cn'])
                %if 'desc' in u and u['desc']:
                %lh.append('<dt>desc</dt><dd title="description">&nbsp;%s</dd>' % u['desc'])
                %end
                %if 'manager' in u:
                    %lm = [ '<a href="/user/%(dir)s">%(dir)s</a>' % {'dir': m} for m in u['manager']]
                    %if len(lm) > 1: 
                        %m_st = 'directeurs'
                    %else:
                        %m_st = 'directeur'
                    %end
                    %lh.append('<dt>%s</dt><dd>' % m_st + ', '.join(lm) + '</dd>')
                %end
                %s += '&nbsp;<button title="ouvrir" class="toggle btn btn-mini" value="+"/>+</button><div class="toggle-item"><dl class="dl-horizontal">' + ' '.join(lh) + '</dl></div>'
                %lp.append(s)    
            %end
            %sm = ' &nbsp;&bull;&nbsp; '.join(lp)
            {{!sm}}
            </dd>
        </dl>
        <dl class="dl-horizontal">
        %if len(students) == 0:
            <dt>pas de etudiant</dt>
        %elif len(students) == 1:
            <dt>1 etudiant(e)</dt>
        %else:
            <dt>{{len(students)}} etudiant(e)s</dt>
        %end
            <dd>
            %lp = []
            %for u in students:
                %lh = []
                %s = '<a href="/user/%s">%s</a>' % (u['uid'], u['cn'])
                %if 'desc' in u and u['desc']:
                %lh.append('<dt>desc</dt><dd title="description">&nbsp;%s</dd>' % u['desc'])
                %end
                %if 'manager' in u:
                    %lm = [ '<a href="/user/%(dir)s">%(dir)s</a>' % {'dir': m} for m in u['manager']]
                    %if len(lm) > 1: 
                        %m_st = 'directeurs'
                    %else:
                        %m_st = 'directeur'
                    %end
                    %lh.append('<dt>%s</dt><dd>' % m_st + ', '.join(lm) + '</dd>')
                %end
                %s += '&nbsp;<button title="ouvrir" class="toggle btn btn-mini" value="+"/>+</button><div class="toggle-item"><dl class="dl-horizontal">' + ' '.join(lh) + '</dl></div>'
                %lp.append(s)    
            %end
            %sm = ' &nbsp;&bull;&nbsp; '.join(lp)
            {{!sm}}
            </dd>
            <dt>voir tout</dt>
            <dd><button class="btn btn-mini toggle-all">tout ouvrir</button></dd>
        </dl>
    </div><!-- #page -->

    <div id="logs" class="onglet box shadow">
        <h1>{{desc}}<br/><small>LOGS</small></h1>
        <div>Liste chronologique des logs.</div>
        <button id="addlogd">mettre a jour les logs</button>
        <div id="logs-texts"> </div>
    </div><!-- #logs -->

</div><!-- #onglets -->
