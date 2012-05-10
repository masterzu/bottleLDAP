/**********************************************************
 BASE jquery fonction to 
 - research form #input_search
 - link #top to /
 - link #author 
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
 show warning
*/

function show_warning(text) {
    if (text) {
        $('#warning').show('slow').text(text);
        alert(text);
        // close after 20s
        setTimeout("$('#warning').hide('slow')", 20000);
    } else {
        $('#warning').hide('slow');
    }
};

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
                alert("hum ?!");
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

