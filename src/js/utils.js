/*
 * WMArchive utilities
 * Author: Valentin Kuznetsov
 */
function loadContent() {
    html = '<div id="header" class="header shadow"></div><div id="center"></div><div id="footer"></div>';
    $("#content").append(html);
    img = '<img src="/wmarchive/web/static/images/cms_logo.png" alt="" style="width:30px">&nbsp;';
    title = '<h3>' + img + ' CMS WMArchive data-service</h3>'
    $("#header").html('<row centered><column cols="8">' + title + '</column></row>');
    html = '<div id="menu"></div><div id="page"></div>'
    $("#center").html('<row centered><column cols="8">' + html + '</column></row>');
    html = '<blocks col="6">' +
        '<div><button type="black" upper outline onclick="ShowMenu(\'home\')">Home</button></div>' +
        '<div><button type="black" upper outline onclick="ShowMenu(\'apis\')">APIs</button></div>' +
        '<div><button type="black" upper outline onclick="ShowMenu(\'tools\')">Tools</button></div>' +
        '<div><button type="black" upper outline onclick="ShowMenu(\'queries\')">Queries</button></div>' +
        '<div><button type="black" upper outline onclick="ajaxRequestStatus();ajaxRequestJobs();ShowMenu(\'jobs\')">Jobs</button></div>' +
        '<div><button type="black" upper outline onclick="ShowMenu(\'stats\')">Stats</button></div>';
    $("#menu").html(html);
    home    = '<div id="home" class="show"></div>';
    apis    = '<div id="apis" class="hide"></div>';
    tools   = '<div id="tools" class="hide"></div>';
    queries = '<div id="queries" class="hide"></div>';
    jobs    = '<div id="jobs" class="hide"></div>';
    stats   = '<div id="stats" class="hide"></div>';
    html    = '<div>' + home + apis + tools + queries + jobs + stats + '</div>';
    $("#page").html(html);
    var today = new Date();
    html = 'CMS collaboration: ' + today;
    $("#footer").html('<row centered><column cols="10">' + html + '</column></row>');
    $("#footer").css("text-align", "center");
	// load templates in their div containers
    $("#home").load("/wmarchive/web/static/templates/home.html");
    $("#apis").load("/wmarchive/web/static/templates/apis.html");
    $("#tools").load("/wmarchive/web/static/templates/tools.html");
    $("#queries").load("/wmarchive/web/static/templates/queries.html");
    $("#jobs").load("/wmarchive/web/static/templates/jobs.html");
    $("#stats").load("/wmarchive/web/static/templates/stats.html");
}
function ShowMenu(tag) {
    HideTag('home');
    HideTag('apis');
    HideTag('tools');
    HideTag('queries');
    HideTag('jobs');
    HideTag('stats');
    ShowTag(tag);
}
function updateTag(tag, val) {
   var id = document.getElementById(tag);
   if (id) {
       id.value=val;
   }
}
function ClearTag(tag) {
    var id=document.getElementById(tag);
    if (id) {
        id.innerHTML="";
    }
}
function HideTag(tag) {
    var id=document.getElementById(tag);
    if (id) {
        id.className="hide";
    }
}
function ShowTag(tag) {
    var id=document.getElementById(tag);
    if (id) {
        id.className="show";
    }
}
function FlipTag(tag) {
    var id=document.getElementById(tag);
    if (id) {
        if  (id.className == "show") {
            id.className="hide";
        } else {
            id.className="show";
        }
    }
}
function ToggleTag(tag, link_tag) {
    var id=document.getElementById(tag);
    if (id) {
        if  (id.className == "show") {
            id.className="hide";
        } else {
            id.className="show";
        }
    }
    var lid=document.getElementById(link_tag);
    if (lid) {
        if  (lid.innerHTML == "show") {
            lid.innerHTML="hide";
        } else {
            lid.innerHTML="show";
        }
    }
}
function load(url) {
    window.location.href=url;
}
function reload() {
    load(window.location.href);
}
function ajaxRequestStatus() {
    var request = $.ajax({
        url: '/wmarchive/data/?status=1',
        contentType: "application/json",
        type: 'GET',
        cache: false,
    });
    request.done(function(data, msg, xhr) {
        var html = '';
        var res = data.result;
        for(var i=0; i<res.length; i++) {
            var d = res[i].status;
            var sts = d.sts;
            var lts = d.lts;
            html += '<h5>Short-Term Storage</h5>\n';
            html += 'njobs: '+ sts.njobs + '<br/>\n';
            stats = sts.stats;
            for(key in stats) {
                html += key+': '+stats[key]+'<br/>\n';
            }
            if (lts != null) {
                html += '<h5>Long-Term Storage</h5>\n';
                html += 'qsize: '+ sts.qsize + '<br/>\n';
                html += 'npids: '+ sts.pids + '<br/>\n';
            }
        }
        $('#wmaStatus').html(html);
    });
}
function ajaxRequestJobs() {
    var request = $.ajax({
        url: '/wmarchive/data/?jobs=1',
        contentType: "application/json",
        type: 'GET',
        cache: false,
    });
    request.done(function(data, msg, xhr) {
        var html = '';
        var res = data.result;
        for(var i=0; i<res.length; i++) {
            var jobs = res[i].jobs;
            html += '<h5>Available jobs output:</h5>\n';
            for(var k=0;k<jobs.length;k++) {
                var j = jobs[k];
                html += '<a href="/wmarchive/data/'+j.wmaid+'">'+j.wmaid+'</a><br/>\n';
            }
        }
        $('#wmaJobs').html(html);
    });
}
