%rebase base title="Équipes", nav=nav, warn=warn, author=author, version=version
<div class="box shadow">
<h1>Équipes &amp; Groupes</h1>
<ul>
%for dn, gr in groups:
    <li><span style="font-variant:small-caps; font-weight:bold;">{{gr['cn'][0]}}</span>: <a href="/group/{{gr['cn'][0]}}" title="{{dn}}">{{gr['description'][0]}}</a></li>
%end
</ul>
</div><!-- box shadow -->
