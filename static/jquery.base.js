/**********************************************************
 BASE jquery fonction to 
 - research form #input_search
 - link #top to /
 - link #author 
*/

// add string.capitalize() function
String.prototype.capitalize = function(){
    return this.replace( /(^|\s)([a-z])/g , function(m,p1,p2){ return p1+p2.toUpperCase(); } );
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
 DEBUG with #warning and .change()
*/
    //$('#warning').text('DEBUG ZONE').show();



/**********************************************************
 show warning
*/

    function show_warning(text) {
        $('#warning').show().text(text);
        $('#warning').fadeOut(10000);
    };
    $('#warning').fadeOut('fast');


/**********************************************************
 JQUERY function to add interactivity to 
 - user.tpl
 - group.tpl

 1/ enable «onglet» with #onglets and .onglet class

 2/ enable {span,button}.click() to table#fields span, table#fields button

 3/ enable input.keypress(<ENTER>) to change it with $.getJSON
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

    /********************************************
     Private fonctions
    */

});

