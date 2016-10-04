%rebase base title="Nouveautés", nav=nav, warn=warn, author=author, version=version

%if ver:
<div class="box shadow">
<h1>Nouveautés<br /><small>version {{ver}}</small></h1>
    %ns = list(news[:])
    %ns.reverse()
    %for _version, _date, _texts in ns:
        %if _version==ver:
    <dl class="dl-horizontal">
        <dt>{{_date}}</dt>
        <dd><strong>Version {{_version}}</strong></dd>
        <dd>
            <ul class="news">
                %for _text in _texts:
                <li>{{_text}}</li>
                %end
            </ul>
        </dd>
    </dl>
        %end
    %end
<p>Retour aux <a href="/news">news</a></p>
</div>

%else:

<div class="box shadow">
<h1>Nouveautés du site.</h1>
<dl class="dl-horizontal">
    %ns = list(news[:])
    %ns.reverse()
    %for _version, _date, _texts in ns:
        %if _version == 'TODO':
    <hr/>
    <dt> <a href="/news/{{_version}}">développement futurs</a></dt>
    <dd>
        <ul class="news">
            %for _text in _texts:
            <li> {{_text}} </li>
            %end
        </ul>
    </dd>
        %else:
    <dt> <a href="/news/{{_version}}">{{_date}}</a> </dt>
    <dd><strong>Version {{_version}}</strong></dd>
    <dd>
    <ul class="news">
        %if _texts[0]:
        <li>{{_texts[0]}} <a class="btn btn-mini" href="/news/{{_version}}">+ infos</a></li>
        %end
        </ul>
    </dd>
        %end
    %end
</dl>

</div>
%end

<!-- :vim:ft=html: -->
