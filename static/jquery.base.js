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

    // #fields
    var css_show_inline = { 'display': 'inline'};
    var css_show_block = { 'display': 'block'};
    var css_hide = { 'display': 'none'};

    function set_fields(name, text) {
    // set span.text; input.value; show span; hide input and button
        var span_filters = "span[name='" + name + "']"
        var span_filters_hide = "#fileds span[name='" + name + "']"
        var input_filters = "input[name='" + name + "']"
        var button_filters = "button[name='" + name + "']"

        $(span_filters).css(css_show_inline);
        if (text) {
            $(span_filters).removeClass('warning').text(text);
            $(input_filters).val(text);
        } else {
            $(span_filters_hide).addClass('warning');
            $(span_filters).text('vide');
            $(input_filters).val('');
        }
        $(span_filters_hide).css(css_hide);
        $(button_filters).css(css_hide);
    };
    
    // #fields span.click()
    $('table#fields span').click(function () {
        $(this).css(css_hide).next().css(css_show_inline).next().css(css_show_inline);
    });

    // #fields input keypress=<enter> 
    $('table#fields input').keypress(function(e) {
        if ((e.which == 13) && $(this).val() != '') {
            var attr = $(this).attr('name');
            var this_span = $(this).prev('span');
            var this_input = $(this);
            var this_button = $(this).next('button');
            var oldval = this_span.val();
            var newval = $(this).val();
            /*
            Only handle the first value
            var vals = new Array();
            $("table#fields input[id*='"+attr+"']").each(function(){
                vals.push($(this).val());
            });
            alert('vals='+vals);
            */
            var url = '/api/user/' + $('#uid').text() + '/attr/' + attr;

            // post ajax
            $.post(url,{'attr': attr, 'newval': newval},function(data, textStatus){
                if (textStatus == 'success') { // ajax OK
                    //alert('OK JSON='+data[attr]);
                    if (! data['success']) {
                        show_warning(data['message']);
                        set_fields(attr, this_span.val());
                        
                    } else {
                        newval = data[attr];
                        set_fields(attr, newval);
                        this_span.show();
                        this_input.hide();
                        this_button.hide();

                    }

                } else {
                    show_warning('AJAX: error: POST '+url);
                    set_fields(attr, this_span.val());
                };
            } ,'json');
        };
    /*
    }).change(function(){
        // DEBUG with #warning
        $('#warning').text($(this).attr('id')+':'+$(this).val());
    */
    });

    // #fields button[reset].click()
    $("table#fields button[value=reset]").click(function(){
        var attr = $(this).attr('name');
        var this_span = $(this).prev().prev();
        var this_input = $(this).prev();
        var this_button = $(this);
        var url = '/api/user/' + $('#uid').text() + '/attr/' + attr;

        // load in span
        $.getJSON(url,function(data, textStatus){
            if (textStatus == 'success') { // ajax OK
                //alert('OK JSON='+data[attr]);
                var text = data[attr];
                set_fields(attr, text);
                this_span.show();
                this_input.hide();
                this_button.hide();

            } else { //ajax error
                show_warning('AJAX: error: GET '+url);
                var text = this_span.val();
                set_fields(attr, text);
            };

        });
    });

    /********************************************
     Private fonctions
    */

});

