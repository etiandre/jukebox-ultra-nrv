import html
import re, requests
import json
from html.parser import HTMLParser
from flask import current_app as app
from flask import session

class BandcampParser(HTMLParser):
	def __init__(self):
		super().__init__()
		self.track_informations = {}
	def handle_starttag(self, tag, attrs):
		is_image = False;
		for item in attrs:
			if (item[0] == 'rel' and item[1] == 'image_src'):
				is_image = True;
			elif (is_image and item[0] == 'href'):
				self.track_informations["image"]=item[1]
	def handle_endtag(self, tag):
		pass

	def handle_data(self, data):
		index_ad_b=data.find("var TralbumData")
		if index_ad_b >= 0:
			index_ad_e=data.find("};", index_ad_b)
			albumData=data[index_ad_b:index_ad_e+2]
			index_ti_b=albumData.find("trackinfo: [{")
			index_ti_e=albumData.find("}]", index_ti_b)
			track_info=json.loads(albumData[index_ti_b+12:index_ti_e+1])
			self.track_informations["title"]=track_info["title"]
			self.track_informations["length"]=track_info["duration"]
			# on repère le nom d'artiste comme étant une chaine de la forme 'artist: "*",' ce qui peut poser problème si le nom d'artiste comporte '",'
			index_artist_b=albumData.find("artist: \"")
			index_artist_e=albumData.find("\",", index_artist_b)
			self.track_informations["artist"]=albumData[index_artist_b+9:index_artist_e]

def search(query):
    """
    Search for a bandcamp url
    """
    results = []
    parser = BandcampParser()
    response = requests.get(query) # response : Response
    parser.feed(response.text)
    results.append({
        "source": "bandcamp",
        "title": parser.track_informations["title"],
        "artist": parser.track_informations["artist"],
        "url": query,
        "albumart_url": parser.track_informations["image"],
        "duration": parser.track_informations["length"],
        "id": 42
        })
    return results
