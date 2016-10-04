Raphael.fn.pieChart = function (cx, cy, r, values, labels, quotas, graces, title) {
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


    var angle = 0,
        total = 0,
        start = 0,
        process = function (j) {
            var value = values[j],
                value_human = kilobytesToSize(value),
                login = labels[j],
                angleplus = 360 * value / total,
                popangle = angle + (angleplus / 2),
                ms = 500,
                delta = 20,
                user_dx = - r * 1.1 * Math.cos(-popangle * rad),
                user_dy = - r * 1.1 * Math.sin(-popangle * rad),
                color = Raphael.hsb(start, 0.5, 1),
                // h' = h + 180deg (ou + .5) ; s' = (v.s)/(v.(s-1)+1) ; v' = v.(s-1)+1
                // http://fr.wikipedia.org/wiki/Teinte_Saturation_Valeur#Couleurs_compl.C3.A9mentaires
                bcolor = Raphael.hsb(start, 1, 1),
                bcolor_comp = Raphael.hsb(start + 0.5, 1, 1),
                sector_fillcolor = quotas[j] ?
                    '-' + [bcolor, bcolor_comp, bcolor, bcolor_comp, bcolor, bcolor_comp, bcolor, bcolor_comp, bcolor, bcolor_comp, bcolor].join('-') : 
                    "-" + bcolor + "-" + color,
                user_anim = quotas[j] ?
                    {transform: "s3", fill: "#f00", stroke: "#000", opacity: 1} :
                    {transform: "s2", fill: "#fff", stroke: "#000", opacity: 1},
                user_size_text = quotas[j] ?
                    value_human + '(' + graces[j] + ')' : 
                    value_human,
                user_size_anim = quotas[j] ? 
                    {transform: "s3", opacity: 1, fill: "#f00", stroke: "#000"} :
                    {transform: "s2", opacity: 1, fill: "#fff", stroke: "#000"},
                p = sector(cx, cy, r, angle, angle + angleplus, 
                    {fill: (angle+angleplus/2) + sector_fillcolor, stroke: "#fff", "stroke-width": 3}).attr('cursor', 'pointer'),
                user = paper.text(cx - user_dx, cy - user_dy, labels[j]).attr({fill: "#000", stroke: "none", "font-size": 13, opacity: 0}).hide(),
                user_size = paper.text(cx, cy, user_size_text).attr({fill: "#000", stroke: "none", "font-size": 15, opacity: 0}).hide();
                //#center# user_size = paper.text(cx, cy, value_human).attr({fill: "#000", stroke: "none", opacity: 0, "font-size": 15});
                //#under text# user_size = paper.text(cx - user_dx, cy - user_dy + 2*delta , value_human).attr({fill: "#000", stroke: "none", opacity: 0, "font-size": 15});
                //#inner circle# user_size = paper.text(cx + (r + delta * 2 ) * Math.cos(-popangle * rad), cy + (r + delta * 2) * Math.sin(-popangle * rad), value_human).attr(user_size_attr);

            p.mouseover(function () {
                p.stop().animate({transform: "s1.1 1.1 " + cx + " " + cy}, ms, "elastic");
                user.show().stop().animate(user_anim, ms/4, ">").toFront();
                user_size.show().stop().animate(user_size_anim, ms/4, ">").toFront();
            }).mouseout(function () {
                var visible = angleplus > 10 ? true : false;
                p.stop().animate({transform: ""}, ms, "elastic");
                user.show().stop();
                if (visible) {
                    user.animate({transform: "", stroke: "none", fill: "#000"}, ms, "bounce");
                } else {
                    user.animate({transform: "", stroke: "none", fill: "#000", opacity: 0}, ms, "bounce");
                }
                user_size.show().stop().animate({transform: "", opacity: 0, stroke: "none", fill: "#000"}, ms);
            }).click(function(){
                var url = '/user/'+login;
                $(location).attr('href', url);
                
            });
            if (angleplus > 10) {
                user.attr({opacity: 1}).show();
            }
            chart.push(p);
            chart.push(user);
            chart.push(user_size);
            angle += angleplus;
            start += 0.1;
        },
        thetitle,
        thesize;

    // calculate total files
    for (var i = 0, ii = values.length; i < ii; i++) {
        total += values[i];
    }
    // calculate thetitle w/ total
    thetitle = paper.text(15, 15, title).attr({fill: "#000", stroke: "none", "font-size": 25, 'text-anchor': 'start'});
    thesize = paper.text(15, 40, "(total du Top: "+kilobytesToSize(total,2)+")").attr({fill: "#000", stroke: "none", "font-size": 15, 'text-anchor': 'start'});
    chart.push(thetitle);

    // plot pies
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
