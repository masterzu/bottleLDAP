Raphael.fn.pieChart = function (cx, cy, r, values, labels, title) {
    var paper = this,
        rad = Math.PI / 180,
        chart = this.set();
    function sector(cx, cy, r, startAngle, endAngle, params) {
        var x1 = cx + r * Math.cos(-startAngle * rad),
            x2 = cx + r * Math.cos(-endAngle * rad),
            y1 = cy + r * Math.sin(-startAngle * rad),
            y2 = cy + r * Math.sin(-endAngle * rad);
        return paper.path(["M", cx, cy, "L", x1, y1, "A", r, r, 0, +(endAngle - startAngle > 180), 0, x2, y2, "z"]).attr(params);
    }

    // http://codeaid.net/javascript/convert-size-in-bytes-to-human-readable-format-(javascript)
    function kilobytesToSize(kilobytes, precision) {  
        var kilobyte = 1,
            megabyte = kilobyte * 1024,
            gigabyte = megabyte * 1024,
            terabyte = gigabyte * 1024;
       
        if ((kilobytes >= 0) && (kilobytes < kilobyte)) {
            return kilobytes + ' o';
     
        } else if ((kilobytes >= kilobyte) && (kilobytes < megabyte)) {
            return (kilobytes / kilobyte).toFixed(precision) + ' Ko';
     
        } else if ((kilobytes >= megabyte) && (kilobytes < gigabyte)) {
            return (kilobytes / megabyte).toFixed(precision) + ' Mo';
     
        } else if ((kilobytes >= gigabyte) && (kilobytes < terabyte)) {
            return (kilobytes / gigabyte).toFixed(precision) + ' Go';
     
        } else if (kilobytes >= terabyte) {
            return (kilobytes / terabyte).toFixed(precision) + ' To';
     
        } else {
            return kilobytes + ' Ko';

        }
    };

    var angle = 0,
        total = 0,
        start = 0,
        process = function (j) {
            var value = values[j],
                value_human = kilobytesToSize(value),
                login = labels[j],
                angleplus = 360 * value / total,
                popangle = angle + (angleplus / 2),
                color = Raphael.hsb(start, .75, 1),
                ms = 500,
                delta = 20,
                user_dx = - (r - delta) * Math.cos(-popangle * rad),
                user_dy = - (r - delta) * Math.sin(-popangle * rad),
                bcolor = Raphael.hsb(start, 1, 1),
                p = sector(cx, cy, r, angle, angle + angleplus, 
                    {fill: "90-" + bcolor + "-" + color, stroke: "#fff", "stroke-width": 3}).attr('cursor', 'pointer'),
                user = paper.text(cx - user_dx, cy - user_dy, labels[j]).attr({fill: "#000", stroke: "none", "font-size": 13}),
                user_size = paper.text(cx + (r + delta * 2 ) * Math.cos(-popangle * rad), cy + (r + delta * 2) * Math.sin(-popangle * rad), value_human).attr({fill: bcolor, stroke: "none", opacity: 0, "font-size": 15});

            p.mouseover(function () {
                p.stop().animate({transform: "s1.1 1.1 " + cx + " " + cy}, ms, "elastic");
                //user.stop().animate({transform: "t"+user_dx+","+user_dy+"s2"}, ms/4, ">").toFront();
                user.stop().animate({transform: "s2"}, ms/4, ">").toFront();
                user_size.stop().animate({opacity: 1, "font-size": 20}, ms/4, ">");
            }).mouseout(function () {
                p.stop().animate({transform: ""}, ms, "elastic");
                user.stop().animate({transform: ""}, ms, "bounce");
                user_size.stop().animate({opacity: 0, "font-size": 15}, ms);
            }).click(function(){
                var url = '/user/'+login;
                $(location).attr('href', url);
                
            });
            angle += angleplus;
            chart.push(p);
            chart.push(user);
            chart.push(user_size);
            start += .1;
        },
        thetitle = paper.text(15, 15, title).attr({fill: "#000", stroke: "none", "font-size": 25, 'text-anchor': 'start'}),
        thetitle_w = thetitle.getBBox()['width'],
        thetitle_h = thetitle.getBBox()['height'];

    // place the title
    //thetitle.transform('t'+X+',0');
    chart.push(thetitle);

    for (var i = 0, ii = values.length; i < ii; i++) {
        total += values[i];
    }
    for (i = 0; i < ii; i++) {
        process(i);
    }
    return chart;
};
/*
$(function () {
    var values = [],
        labels = [],
        graph_size = 400,
        pie_pos = graph_size / 2,
        pie_size = graph_size / 3;
    //alert(new Array(graph_size, pie_pos, pie_size).join(', '));
    $("#pie-datas tr").each(function () {
        labels.push($("th", this).text());
        values.push(parseInt($("td", this).text(), 10));
    });
    $("#pie-datas").hide();
    Raphael("pie", graph_size, graph_size).pieChart(pie_pos, pie_pos, pie_size, values, labels);

});
*/
