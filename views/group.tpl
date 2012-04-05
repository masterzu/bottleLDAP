%rebase base title="Équipes : %s" % cn , nav=nav, warn=warn, author=author, version=version
<div class="box shadow">
<h1>Groupe {{cn}}</h1>
<dt>
    %if desc:
    <dt>Description</dt>
    <dd>{{desc}}</dd>
    %end

    <dt>{{len(members)}} membres</dt>
    %for u in members:
    <dd><a href="/user/{{u['uid']}}">{{u['cn']}}</a> </dd>
    %end
</dt>
</div><!-- box shadow -->
