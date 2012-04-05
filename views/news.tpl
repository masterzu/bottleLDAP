%rebase base title="Nouveautés", nav=nav, warn=warn, author=author, version=version

%if ver:
<div class="box shadow">
<h1>Nouveautés de la version {{ver}}</h1>
    %ns = list(news[:])
    %ns.reverse()
    %for _version, _date, _texts in ns:
        %if _version==ver:
    <dl>
        <dt><strong>Date:</strong> {{_date}}</dt>
        <dt><strong>Version:</strong> {{_version}}</dt>
    <dl>
    <ul>
        %for _text in _texts:
        <li>{{_text}}</li>
        %end
    </ul>
        %end
    %end
</div>
<p>Retour aux <a href="/news">news</a></p>




%else:

<div class="box shadow">
<h1>Nouveautés du site.</h1>
<dl>
    %ns = list(news[:])
    %ns.reverse()
    %for _version, _date, _texts in ns:
        %if _version == 'TODO':
    <hr/>
    <dt> <a href="/news/{{_version}}">développement futurs</a> : </dt>
            %for _text in _texts:
    <dd> {{_text}} </dd>
            %end
        %else:
    <dt> <a href="/news/{{_version}}">{{_date}}</a> <strong>version {{_version}}</strong> : </dt>
            %for _text in _texts:
    <dd> {{_text}} </dd>
            %end
        %end
    %end
</dl>

</div>
%end
