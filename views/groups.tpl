%rebase base title="Équipes", nav=nav, warn=warn, author=author, version=version

<script type="text/javascript">
<!--

$(function() {
    %for dn, gr in groups:
	%code = gr['cn'][0]
        $('a#infos-{{code}}').click(function() { ajax_button_span_url($(this), $('span#infos-{{code}}'), '/api/group/{{code}}/members') });
    %end
});
// -->
</script>

<div class="box shadow">
<h1>Équipes &amp; Groupes</h1>
%for dn, gr in groups:
    %code = gr['cn'][0]
<h3>{{gr['description'][0]}}</h3>
<dl class="dl-horizontal">
    <dt>lien</dt>
    <dd><a href="/group/{{gr['cn'][0]}}" title="{{dn}}">{{gr['description'][0]}}</a></dd>
    <dt>code</dt>
    <dd><code>{{code}}</code></dd>
    <dt> <a id="infos-{{code}}" class="btn btn-mini">+infos</a> </dt>
    <dd> <span id="infos-{{code}}">&nbsp;</span> </dd>


</dl>
%end
</div><!-- box shadow -->
