%rebase base title='', nav=nav, warn=warn, author=author, version=version
%#
%# Vars: cn, desc, members, phds, students
%#
<div class="box shadow">
<h1>Bienvenue sur <strong>bottleLDAP</strong></h1>

<p>Ce projet a un double objectif.
<strong>Cuisiner</strong> un site web <em>minimaliste</em> (sans apache ou autre <em>Guerrier du web</em>) et autre ingrédients en <em>webdesign</em>.
<p>Et accessoirement, pouvoir <strong>administrer</strong> le serveur <strong>LDAP</strong> de l'Institut <code>:-P</code>.</p>
<h2>News</h2>
%l = list()
%ns = list(news[:])
%ns.reverse()
%first = True
%for version, date, list_texts in ns:
    %if first:
        <p>Dernière version du <a href="/news/{{version}}">{{date}}</a> (version {{version}}):</p>
        %for text in list_texts:
        <dd>{{text}}</dd>
        %end
        %first = False
    %else:
        %if version != 'TODO':
            %l.append('<a href="/news/%s" title="%s">%s</a>' % (version,list_texts[0],date))
        %end
    %end
%end
%s = ', '.join(l)
    <p> Autres versions: {{!s}} </p>
</div>

<!-- :vim:ft=html: -->
