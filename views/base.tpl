%#
%# Vars: title, warn, version, author, nav
%#
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html>
<head>
  <title>{{"bottleLDAP | " + title or 'No title'}}</title>
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <link rel="stylesheet" type="text/css" href="/static/all.css" />
  <link rel="shortcut icon" href="/static/favicon.ico" />
  <script src="/static/all.min.js"></script>
</head>
<body>

    <div id="top">
        <div id="top-container" class="container">
            <div class="row">
                <div id="top-logo" class="span3">&nbsp;</div>
                <div id="top-content" class="span9">
                    {{title or "Administration LDAP"}}
                </div><!-- top-content -->
            </div>
        </div><!-- top-container -->
    </div><!-- top -->
    <div id="content-container" class="container">
    <div id="content-center" class="row">
        <div id="nav" class="span3">
            %if nav is not None:
            <ul class="nav nav-list">
                %for (l, n) in nav:
                    %if l == '*' and n:
                <li class="nav-title">{{n}}</li>
                    %elif l == '_SEARCH_':
                <li><input class=".span3" placeholder="{{n}}" type="text" name="search" id="input_search"/></li>
                    %elif l and n:
                <li><a href="{{l}}">{{n}}</a></li>
                    %elif n:
                <li class="active">{{n}}</li>
                    %else:
                <li class="diviser">&nbsp;</li>
                    %end
                %end
            </ul>
            %else:
            <div class="label label-important">No navigation links available</div>
            %end
        </div><!-- nav -->
        <div id="content" class="span9">
            <div id="warning" style="display:none;"></div>
            %if warn:
                <script>show_warning('{{!warn}}'); </script>
            %end
            <div id="content-text">
<!------------------------------ -->
<!-- BEGIN INCLUDE from base.tpl -->

            %include

<!-- END   INCLUDE from base.tpl -->
<!------------------------------ -->
            </div><!-- content-text -->
        </div><!-- content -->
    </div><!-- content-center -->
    <div id="bottom" class="row">
        <div class="span12">
        bottleLDAP {{version}} 
        &bull; 
	    &copy; <span id="author">{{author}}</span>, 2011&ndash;2017
        &bull; 
        illustré par <a href="http://dmitrybaranovskiy.github.io/raphael/" target="_raph">Raphaël JS</a>
        &bull; 
        animé par <a href="http://jquery.com" target="_jquery">jQUERY</a>
        &bull; 
        propulsé par <a href="http://bottlepy.org/docs/0.12/" target="_bottle">bottle</a> 
        &bull; 
        coagulé par <a href="http://www.python-ldap.org/" target="_pyldap">python-ldap</a>
        </div><!-- #bottom -->
    </div>
    </div><!-- #content-container -->
    <div id="bottom-clear"></div>
</body>
</html>

<!-- vim:set ft=html: -->
