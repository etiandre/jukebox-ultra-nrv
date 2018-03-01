function template(html, d) {
	var r = html;
	for (i in d) {
		r=r.replace("{"+i+"}", d[i]);
	}
	r=r.replace(/{\w+}/g, "")
	return r;
}

function generate_track_html(t) {
	track_html = document.createElement("div")
	track_html.innerHTML = template(track_template, t)		
	$(track_html).children().data("track", t);
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
		<span class="track-user float-right">ajouté par {user}</span>
	</div>
	<div class="col-1 centered">
		<img class="icon btn-remove" alt="Enlever" src="/static/images/icons/x.svg">
	</div>

</div>
</li>
`
sync = function() {
	$.get("/sync", function (data) {
		// console.log(data);
		$('#volume-slider').val(data.volume);
		$('#playlist').html("");
		for (i in data.playlist) {
			var t = data.playlist[i];
			if (i == 0) {
				$('#playlist').append("<p class='playlist-title'>Lecture en cours</p>")
			}
			else if (i == 1) {
				$('#playlist').append("<p class='playlist-title'>À venir</p>")
			}
			$('#playlist').append(generate_track_html(t))
			$('#playlist li:last .btn-remove').click(function() {
				$.post("/remove", $(this).parents("li").data("track"));
				$(this).parents("li").hide();
			});
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

$('#query').keyup(function() {
	if ($('#query').val() == "") {
		$("#search_results").html("");
		$("#search_results").hide();
		return;
	}
	delay(function() {
		console.log("searching "+$('#query').val());
		$.post("/search", {"q": $('#query').val()}, function(data) {
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
	},150);
});
$('#query').focus(function () {
	if ($('#query').val() != "")
		$('#search_results').show();
});

$("#volume-slider").change(function() {
	$.post("/volume", {"volume": $(this).val()})
})

$('#search_results').hide();