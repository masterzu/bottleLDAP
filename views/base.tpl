<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html>
<head>
  <title>{{"bottleLDAP | " + title or 'No title'}}</title>
  <link rel="stylesheet" type="text/css" href="/static/base.css" />

  <link rel="shortcut icon" href="/static/favicon.ico" />
</head>
<body>
    <script src="/static/jquery.1.7.1.min.js"></script>
    <script src="/static/jquery.tablesorter.min.js"></script><!-- http://tablesorter.com/docs/ -->
    <script src="/static/jquery.base.js"></script><!-- research engine -->
    <div id="top-container">
    <div id="top-center">
        <div id="top">
        </div><!-- top -->
        <div id="top-content">
            {{title or "Administration de l'annuaire LDAP"}}
        </div><!-- top-content -->
    </div><!-- top-center -->
    </div><!-- top-container -->
    <div id="content-container">
    <div id="content-center">
        <div id="nav" class="box">
            %if nav is not None:
            <ul>
                %for (l, n) in nav:
                    %if l == '*' and n:
                <li class="nav-title">{{n}}</li>
                    %elif l == '_SEARCH_':
                <li><input type="text" name="search" value="{{n}}" id="input_search"/></li>
                    %elif l and n:
                <li class="nav-top"><a href="{{l}}">{{n}}</a></li>
                    %elif n:
                <li class="nav-here">{{n}}</li>
                    %else:
                <li class="separator">&nbsp;</li>
                    %end
                %end
            </ul>
            %else:
            <div class="warning">No navigation links available</div>
            %end
        </div><!-- nav -->
        <div id="content">
            %if warn:
                <div id="warning">{{!warn}}</div>
            %else:
                <div id="warning" style="display:none;"></div>
            %end
<!------------------------------ -->
<!-- BEGIN INCLUDE from base.tpl -->

            <div id="content-text">
            %include
            </div><!-- content-text -->

<!-- END   INCLUDE from base.tpl -->
<!------------------------------ -->
        </div><!-- content -->
        <div id="bottom">
	    &copy; 2011&ndash;2012 <span id="author">{{author}}</span> &bull; bottledap v{{version}} &bull; propulsé par <a href="http://bottlepy.org/docs/0.10/">bottlepy</a>
        </div><!-- bottom -->
    </div><!-- content-center -->
    </div><!-- content-container -->
    <div id="bottom-clear"></div>
</body>
</html>
