function template(html, d) {
	var r = html;
	for (i in d) {
		r=r.replace("{"+i+"}", d[i]);
	}
	r=r.replace(/{\w+}/g, "")
	return r;
}

function generate_track_html(t) {
	track_html = $("<div></div>")
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
		<span class="track-user float-right">ajouté par {user}</span>
	</div>
	<div class="col-1 centered">
		<img class="icon btn-remove" alt="Enlever" src="/static/images/icons/x.svg">
	</div>

</div>
</li>
`

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

serverTime = 0;
function sleep (time) {
  return new Promise((resolve) => setTimeout(resolve, time));
}
function syncVideo() {
	if (serverTime == 0) {
		yt.pauseVideo();
	} else {
		ytTime = yt.getCurrentTime();
		yt.playVideo();
		delta = ytTime - serverTime;
		if (Math.abs(delta) > 1) {
			console.log("catching up");
			yt.seekTo(serverTime);
		}

		else if (delta > 0.05) {
			console.log("en avance de", delta);
			yt.pauseVideo();
			sleep(delta/2).then(() => {
				yt.playVideo();
			});

		}
		else if (delta < -0.1) {
			console.log("en retard de", delta);
			yt.seekTo(serverTime - delta/2);
		}
	}
}

sync = function() {
	time = Date.now() / 1000
	$.get("/sync", function (data) {
		// console.log(data);
		$('#volume-slider').val(data.volume);
		playlistHTML = $("<div></div>")
		//$('#playlist').html("");
		for (i in data.playlist) {
			var t = data.playlist[i];
			if (i == 0) {
                if (yt.ready && $("#YT").is(":visible")) {
                    if (yt.url != data.playlist[0]["id"]) {
                        console.log("loading video", data.playlist[0]["id"])
                        yt.cueVideoById(data.playlist[0]["id"])
                        yt.url = data.playlist[0]["id"]
                    }
					serverTime = data.time + (Date.now()/1000-time)/2;
					syncVideo();
                }
				playlistHTML.append("<p class='playlist-title'>Lecture en cours</p>")
			}
			else if (i == 1) {
				playlistHTML.append("<p class='playlist-title'>À venir</p>")
			}
			playlistHTML.append(generate_track_html(t))
			console.log(playlistHTML.find('li:last .btn-remove'))
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
