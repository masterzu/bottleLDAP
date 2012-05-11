%rebase base title='', nav=nav, warn=warn, author=author, version=version
<div class="box shadow">
<h1>Bienvenue Administration sur l'annuaire LDAP <em>version (beta)</em></h1>

<h2>News</h2>
%l = list()
%ns = list(news[:])
%ns.reverse()
%first = True
%for v, d, l_t in ns:
    %if first:
        <p>Dernière version du <a href="/news/{{v}}">{{d}}</a> (version {{v}}):</p>
        %for t in l_t:
        <dd>{{t}}</dd>
        %end
        %first = False
    %else:
        %if v != 'TODO':
            %l.append('<a href="/news/%s" title="%s">%s</a>' % (v,l_t[0],d))
        %end
    %end
%end
%s = ', '.join(l)
<p> Autres versions: {{!s}} </p>
</div>
