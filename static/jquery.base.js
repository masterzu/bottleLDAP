/**********************************************************
 String extented:
 - capitalize()
 - trim()
*/

// http://stackoverflow.com/questions/1026069/capitalize-the-first-letter-of-string-in-javascript
// from Murat Kucukosman
String.prototype.capitalize = function(){
    return this.replace( /(^|\s)([a-z])/g , function(m,p1,p2){ return p1+p2.toUpperCase(); } );
};

// http://snippets.dzone.com/posts/show/701
// from cornflakesuperstar
String.prototype.trim = function() { 
    return this.replace(/^\s+|\s+$/g, ''); 
};

/**********************************************************
 jQuery extented:
 - center()
*/

// http://stackoverflow.com/questions/210717/using-jquery-to-center-a-div-on-the-screen
// from Tony L + PCHT
// WARNING: dont work with .hide('slow') just before
jQuery.fn.center = function () {
    this.append('<div>[<a href="#">fermer</a>]</div>');
    var w = 400, 
        h = this.outerHeight(),
        t = (Math.max(0, (($(window).height() - h) / 2) + $(window).scrollTop()) + "px"),
        l = (Math.max(0, (($(window).width() - w) / 2) + $(window).scrollLeft()) + "px"),
        calc = $('#pieblack');
    //alert('top:'+t+', left:'+l);
    calc.show();
    this.css({
        "position": "absolute",
        "top": t,
        "left": l
        });
    //this.height(h);
    // set width
    //this.width(w);
    // add fermer link
    $('a',this).click(function(){ calc.hide(); });
    return this;
}


/**********************************************************
 ajax functions
*/


// general function to handle button/span/url
// button && span not null: print message in span
// button not null && spann null: change class to button
function ajax_button_span_url(button, span, url){
    var this_button = button;
    var this_span = span;

    if (button == null && span == null) {
        show_warning('ERROR in ajax_button_span_url: null !');
        return;
    }

    //hide warning
    show_warning();

    //alert('serveur {{name}} with url:'+url);
    if (this_span != null) this_span.addClass('ui-autocomplete-loading').html('&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;');

    // do the ajax job with a timeout
    $.ajax({
        url: url,
        type: "GET",
        dataType: "json",
        timeout: 1500,
        success: function(response) {
            if (this_span != null) this_span.removeClass('ui-autocomplete-loading').text('');
            if (response['success']) {
                if (this_span != null)
                    this_span.text(response['message'])
                else
                    this_button.addClass('widget_ok').removeClass('widget_notok');
            } else {
                if (this_span != null)
                    show_warning(response['message'])
                else
                    this_button.addClass('widget_notok').removeClass('widget_ok');
            }
        },
        error: function(xhr, textStatus, error) {
            this_span.removeClass('ui-autocomplete-loading').text('');
            if (textStatus == "timeout")
                show_warning('Serveur Timeout ... Réessayez si vous osez :)')
            else 
                show_warning('Erreur de serveur: '+error+' ('+textStatus+')');
        }
    });
}; 


/**********************************************************
 show warning
*/

function show_warning(text) {
    if (text) {
        $('#warning').show('slow').text(text);
        // close after 20s
        setTimeout("$('#warning').hide('slow')", 20000);
        //alert(text);
    } else {
        $('#warning').hide('slow');
    }
};

/**********************************************************
 BASE jquery fonction to 
 - research form #input_search
 - link #top to /
 - link #author 
*/

$(function(){
    // search input
    $("#input_search").keypress(function(e){
        if (e.which == 13) {
            var val = $(this).val();
            if (val.match('[*=~]') != null ) {
                alert('ne pas utiliser les caractères *, = ou ~');
            } else if (val != "") {
                window.location='/users/search/'+val;
            } else {
                show_warning("hum ?!");
                $(this).focus();
                return false;
            }
        }
    }).focus(function(){
        $(this).val("");
    }).blur(function(){
        $(this).val("rechercher...");
    });

    // #top link
    $("#top").click(function(){
        window.location='/';
    });

    // #author link
    $("#author").click(function(){
        window.location='/user/pcao';
    });


/**********************************************************
 #warning Zone interactions
*/
    //$('#warning').text('DEBUG ZONE').show();

    $('#warning').fadeOut('fast');
    $('#warning').click(function(){
        $(this).hide('slow');
    });


/**********************************************************
 enable «onglet» with #onglets and .onglet class

*/

    // #onglets - display the first .onglet
    $("#onglets .onglet").not(":first").hide();

    // #onglets.click
    $("#onglets ul a").click(function() {
        $("#onglets .onglet").hide();
        $(this.hash).show();
        this.blur();
        $("#onglets li a").removeClass("actif");
        $(this).addClass("actif");
        return false;
    });

});

