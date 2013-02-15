%rebase base title="Équipes", nav=nav, warn=warn, author=author, version=version
<div class="box shadow">
<h1>Équipes &amp; Groupes</h1>
%for dn, gr in groups:
    <div> 
        <a href="/group/{{gr['cn'][0]}}" title="{{dn}}">{{gr['description'][0]}}</a> (<code>{{gr['cn'][0]}}</code>)
    </div>
%end
</div><!-- box shadow -->
