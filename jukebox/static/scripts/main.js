/*
Script managing the interface.
It uses JQuery
 */

function template(html, d) {
    let r = html;
    for (let i in d) {
        if (i=="title") { // track title appears both on verso and recto
            r=r.replace("{"+i+"}", d[i]);
        }
        r=r.replace("{"+i+"}", d[i]);
    }
    r=r.replace(/{\w+}/g, "");
    return r;
}


function toggle_recto_verso() {
    /*
    Called by a .btn-more or .btn-back
     */
    // console.log("prout");
    let track_li = $(this).closest("li");
    //let id = track_li.attr('id');
    // console.log(id);
    track_li.find(".verso").toggle();
    track_li.find(".recto").toggle();
}


function generate_track_html(t) {
    let track_html = $(template(track_template, t));
    track_html.data("track", t);
    track_html.find(".verso").hide();
    track_html.find(".btn-more").click(toggle_recto_verso);
    track_html.find(".btn-back").click(toggle_recto_verso);
    track_html.find(".btn-up").click(function() {
        $.post("/move-track", {"action": "up", "randomid": t["randomid"]});
    });
    track_html.find(".btn-down").click(function() {
        $.post("/move-track", {"action": "down", "randomid": t["randomid"]});
    });

    track_html.find(".btn-refresh").click(function() {
        $.post("/refresh-track", {"url": t["url"]});
    });

    return track_html
}

function generate_track_html_suggest(t) {
    let track_html = generate_track_html(t);
    track_html.find(".btn-add").click(function() {
        $.post("/add", t); //$(this).parents("li").data("track"));
    });
    track_html.find(".btn-remove").remove();
    track_html.find(".btn-up").remove();
    track_html.find(".btn-down").remove();
    return track_html;
}


function generate_track_html_queue(t) {
    let track_html = generate_track_html(t);
    track_html.find(".btn-remove").click(function() {
        console.log("Removing track with randomid: ", t["randomid"]);
        $.post("/remove", t);//$(this).parents("li").data("track"));
    });
    track_html.find(".btn-add").remove();
    return track_html;
}

track_template = `
<li class="list-group-item track" id="{randomid}">
    <div class="row recto">
        <div class="col-4 centered">
            <img class="albumart" src="{albumart_url}">
        </div>
        <div class="col track-info centered">
            <span class="track-title">{title}</span>
            <span class="track-artist">{artist}</span>
            <span class="track-duration">{duration} s.</span>
            <span class="track-user float-right">Added by {user}</span>
        </div>
        <div class="col-1">
            <button class="icon btn-more" alt="More"></button>
            <button class="icon btn-add" alt="Play"></button>
            <button class="icon btn-up" alt="Up"></button>
            <button class="icon btn-down" alt="Down"></button>
            <button class="icon btn-remove" alt="Enlever"></button>
        </div>
     </div>
     <div class="row verso">
        <div class="col">
            <span class="track-title">{title}</span>
            <span class="track-url"><a href="{url}">Link to media</a></span>
            <span class="track-album">Album : {album}</span>
            <span class="track-source">From {source}</span>
        </div>
        <div class="col-1">
            <button class="icon btn-back" alt="Back"></button>
            <button class="icon btn-refresh" alt="Refresh"></button>
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
    console.log(mpv_time);
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


function updates_playlist(data) {
    // we first get the current playlistHTML
    let playlist = data.playlist;
    let playlistHTML = $("#playlist");
    // then we must check that all elements in playlist are in playlistHTML
    if (playlist.length === 0) {
        playlistHTML.children().remove();
        return;
    }

    for (let i=0; i<playlist.length; i++) {
        let track = playlist[i];
        if (i === 0 && (playlistHTML.find(".track") === 0 || playlistHTML.find(".track:first").attr("id") != track.randomid)) {
            if (playlistHTML.find(".track").length !== 0) {
                playlistHTML.find(".track:first").remove();
            }
            if (playlistHTML.find("#playlist-playing").length !== 0) {
                playlistHTML.find("#playlist-playing").remove();
            }
            playlistHTML.prepend(generate_track_html_queue(track));
            playlistHTML.find(".track:first .btn-down").hide();
            playlistHTML.find(".track:first .btn-up").hide();

            // then we manage the Youtube iframe
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
            if (playlistHTML.find("#playlist-playing").length === 0) { // it doesn't display
                console.log("Adding Lecture en cours");
                playlistHTML.find(".track:first").before("<li id='playlist-playing' class='playlist-title'>Lecture en cours</li>");
            }
        }
        // we do not use !== as the elements are not the same types
        else if (playlistHTML.find(".track:last-child").index < i || playlistHTML.find(".track:eq("+i+")").attr("id") != track.randomid) {
            if (i===1) {
                playlistHTML.find("#playlist-queue").remove();
            }
            playlistHTML.find(".track:eq("+i+")").remove();
            let j = i-1;
            playlistHTML.find(".track:eq("+j+")").after(generate_track_html_queue(track));


            if (playlistHTML.find("#playlist-queue").length === 0) {
                playlistHTML.find(".track:eq(0)").after("<li id='playlist-queue' class='playlist-title'>A venir...</li>");
            }
        }
    }

    // we must remove elements in playlistHTML which are too much
    let i = playlist.length -1;
    //console.log("i: "+i);

    //console.log(playlistHTML.find(".track:eq("+i+")"));
    let track_tile = playlistHTML.find(".track:eq("+i+")");
    //track_tile.css({"color": "red", "border": "2px solid red"});//.nextAll(".track").remove();
    while (track_tile.next().length !== 0) {
        track_tile = track_tile.next();
        track_tile.remove();//css({"color": "green", "border": "2px solid green"});
    }
    /*
    for (let j = i+1; j<playlistHTML.children().length; j++) {
        playlistHTML.find(".track:eq("+j+")").css({"color": "green", "border": "2px solid green"});
    }*/

    /*
    // we removing any surnumary track
    console.log(playlistHTML.children().length); //not good
    for (let i = playlist.length+offset; i<playlistHTML.children(".track")+offset; i++) {
        console.log("Too much tracks, removing "+i);
        playlistHTML.children(":eq(" + i + ")").remove();
    }
    */
}

sync = function() {
    let time = Date.now() / 1000
    $.get("/sync", function (data) {
        $('#volume-slider').val(data.volume);
        updates_playlist(data);
        // TODO : here we reset the playlist, we should not do that
        //let playlistHTML = $("<div></div>");
        //$('#playlist').html("");

        //$("#playlist").html(playlistHTML)
        if (yt !== 0) {
            syncVideo(data.time);
        }
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
            $("#search_results").html("");
            for (let i=0; i<data.length; i++) {
                let track = data[i];
                console.log("Track :");
                console.log(track);
                //track["randomid"] = Math.floor((Math.random() * 999999999999) + 1);
                $('#search_results').append(generate_track_html_suggest(track));
                $('#search_results li:last .btn-add').click(function() {
                    //$.post("/add", track); // we already send an add with the generate_track_html_suggest
                    $('#query').val("");
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
        for (let i =0; i<data.length; i++) {
            let t = data[i];
            $('#suggestions').append(generate_track_html_suggest(t));
        }
    });
}

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


/*
$(document).ready(function hide_recto() {
    $(".verso").hide();
});
*/




$(document).ready(function() {
    suggest();
});
