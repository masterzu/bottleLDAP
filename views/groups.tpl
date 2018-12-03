%rebase base title="Équipes", nav=nav, warn=warn, author=author, version=version
%#
%# Vars: groups
%#

<script type="text/javascript">
<!--

$(function() {
%for dn, gr in groups:
    %code = gr['cn'][0]
    $('a#infos-{{code}}').click(function() { ajax_button_span_url($(this), $('span#infos-{{code}}'), '/api/group/{{code}}/infos') });
    %end
    $('#all').click(function(){
    %for dn, gr in groups:
        %code = gr['cn'][0]
        ajax_button_span_url($('a#infos-{{code}}'), $('span#infos-{{code}}'), '/api/group/{{code}}/infos') 
    %end
    });
});
// -->
</script>

<div class="box shadow">
<h1>Équipes &amp; Groupes</h1>
%for dn, gr in groups:
%code = gr['cn'][0]
<!-- <h3>{{gr['description'][0]}}</h3> -->
<h4><a href="/group/{{gr['cn'][0]}}" title="{{dn}}">{{gr['cn'][0]}} &mdash; {{gr['description'][0]}}</a></h4>
<dl class="dl-horizontal">
    <dt> <a id="infos-{{code}}" class="btn btn-mini">+infos</a> </dt>
    <dd> <span id="infos-{{code}}">&nbsp;</span> </dd>
</dl>
%end
<p>Action: <a id="all" class="btn btn-mini">toutes les infos</a></p>
</div><!-- box shadow -->

<!-- :vim:ft=html: -->
