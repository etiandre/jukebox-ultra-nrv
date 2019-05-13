/*
Script managing the interface.
It uses JQuery
 */

function template(html, d) {
    let r = html;
    for (let i in d) {
        r=r.replace("{"+i+"}", d[i]);
    }
    r=r.replace(/{\w+}/g, "")
    return r;
}

function generate_track_html(t) {
    let track_html = $("<div></div>")
    track_html.html(template(track_template, t))
    track_html.children().data("track", t);
    //console.log(track_html.children().data("track"));
    return track_html
}

track_template = `
<li class="list-group-item">
<div class="row">
        <div class="col-4 centered">
                <img class="albumart" src="{albumart_url}">
        </div>
        <div class="col track-info centered">
                <span class="track-title">{title}</span>
                <span class="track-artist">{artist}</span>
                <span class="track-duration">{duration} s.</span>
                <span class="track-source">{source}</span>
                <span class="track-user float-right">Ajouté par {user}</span>
        </div>
        <div class="col-1 centered">
                <img class="icon btn-remove" alt="Enlever" src="/static/images/icons/x.svg">
        </div>

</div>
</li>
`

// We load the Youtube iframe
var tag = document.createElement('script');
tag.src = "https://www.youtube.com/iframe_api";
var firstScriptTag = document.getElementsByTagName('script')[0];
firstScriptTag.parentNode.insertBefore(tag, firstScriptTag);

var yt = 0;
function onYouTubeIframeAPIReady() {
    yt = new YT.Player('YT', {
        height: '360',
        width: '640',
        events: {
            'onReady': function() {
                console.log("YT ready");
                yt.mute();
                yt.ready = true;

            }
        }
    });
}


function sleep (time) {
    return new Promise((resolve) => setTimeout(resolve, time));
}
function syncVideo(mpv_time) {
    if (mpv_time === 0) {
        yt.pauseVideo();
    } else {
        let ytTime = yt.getCurrentTime();
        yt.playVideo();
        let delta = ytTime - mpv_time;
        if (Math.abs(delta) > 1) {
            console.log("catching up");
            yt.seekTo(mpv_time);
        }
    }
}

sync = function() {
    let time = Date.now() / 1000
    $.get("/sync", function (data) {
        $('#volume-slider').val(data.volume);
        let playlistHTML = $("<div></div>");
        //$('#playlist').html("");
        for (let i=0; i<data.playlist.length; i++) {
            let track = data.playlist[i];
            if (i === 0) {
                if (yt.ready && $("#YT").is(":visible") && track["source"] === "youtube") {
                    let url = new URL(data.playlist[0]["url"]);
                    let videoId = url.searchParams.get("v");
                    let t;
                    if (url.searchParams.has("t")) {
                        t = parseInt(url.searchParams.get("t"), 10);
                    } else {
                        t = 0;
                    }
                    if (yt.url !== videoId) {
                        //console.log("Loading now !");
                        console.log("Loading video with id : ", videoId, " at time ", t);
                        yt.cueVideoById(new String(videoId), t);
                        yt.url = videoId;
                        yt.playVideo();
                    }
                    syncVideo(data.time);
                }
                playlistHTML.append("<p class='playlist-title'>Lecture en cours</p>")
            }
            else if (i == 1) {
                playlistHTML.append("<p class='playlist-title'>À venir</p>")
            }
            playlistHTML.append(generate_track_html(track))
            //console.log(playlistHTML.find('li:last .btn-remove'))
            playlistHTML.find('li:last .btn-remove').click(function() {
                console.log("Deleting track")
                console.log($(this).parents("li").data("track"))
                $.post("/remove", $(this).parents("li").data("track"));
                $(this).parents("li").hide();
                return false;
            });
        }
        $("#playlist").html(playlistHTML)
    });
    window.setTimeout(arguments.callee, 1000);
}();

var delay = (function(){
    var timer = 0;
    return function(callback, ms){
        clearTimeout (timer);
        timer = setTimeout(callback, ms);
    };
})();

$('#query').keyup(function(e) {
    var code = e.which;
    // We make a search **only** if the enter key has been pressed
    if (code != 13) {
        return;
    }
    query = $('#query').val().trim()
    if (query == "") {
        $("#search_results").html("");
        $("#search_results").hide();
        return;
    }
    delay(function() {
        console.log("searching "+$('#query').val());
        $.post("/search", {"q": query}, function(data) {
            $("#search_results").html("")
            console.log(data);
            for (i in data) {
                var t = data[i];
                $('#search_results').append(generate_track_html(data[i]))
                $('#search_results li:last').click(function() {
                    $.post("/add", $(this).data("track"));
                    $('#query').val("")
                    $('#search_results').hide();
                });
            }
            $("#search_results").show()
        }, dataType="json");
        if ($('#query').val() == "") {
            $("#search_results").html("");
            $("#search_results").hide();
            return;
        }
    },250);
});
$('#query').focus(function () {
    if ($('#query').val() != "")
        $('#search_results').show();
});

function suggest() {
    $.get("/suggest", function (data) {
        $('#suggestions').html("");
        for (i in data) {
            var t = data[i];
            $('#suggestions').append(generate_track_html(t))
            $('#suggestions li:last').click(function() {
                $.post("/add", $(this).data("track"));
            });
        }
    });
}
suggest();

$("#volume-slider").change(function() {
    $.post("/volume", {"volume": $(this).val()})
})

$("#refresh-suggestions").click(suggest);
$("#toggle-YT").click(function() {
    $("#YT").toggle();
    if (!$("#YT").is(":visible")) {
        yt.stopVideo();
    } else {
        yt.playVideo();
    }
});

$('#search_results').hide();
