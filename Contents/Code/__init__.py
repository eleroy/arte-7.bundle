VIDEO_PREFIX = "/video/artep7"

VIDEOS_PAGE = 'http://www.arte.tv/guide/%s/'

NAME = 'Arte+7'

ART   = 'art-default.jpg'
ICON  = 'icon-default.png'
PREFS = 'icon-prefs.png'

PREF_STRING = dict({"en":"Preferences","de":"Einstellungen","fr":"Préférences"})

####################################################################################################

def Start():

	Plugin.AddPrefixHandler(VIDEO_PREFIX, VideoMainMenu, NAME, ICON, ART)

	Plugin.AddViewGroup("InfoList", viewMode="InfoList", mediaType="items")
	Plugin.AddViewGroup("List", viewMode="List", mediaType="items")

	MediaContainer.art = R(ART)
	MediaContainer.title1 = NAME
	DirectoryItem.thumb = R(ICON)

	HTTP.CacheTime = 3600

def VideoMainMenu():
	dir = MediaContainer(viewGroup="List",noCache=True)
	mainpage = HTML.ElementFromURL(VIDEOS_PAGE%(Prefs['lang'],)+"plus7")
	for category in mainpage.xpath('//div[@class="choice-by_channel row-fluid choices visible-phone"]/ul[@data-filter="by_channel"]/li[@class="span2"]/a'):
		Log(category.text)
		dir.Append(Function(DirectoryItem(CategoryParsing,category.text,thumb=R(ICON),art=R(ART)),path = category.text.strip()))
	dir.Append(PrefsItem(title=PREF_STRING[Prefs['lang']],subtile="",summary="",thumb=R(PREFS)))
	return dir

def CategoryParsing(sender,path):
	dir = ObjectContainer(view_group='InfoList',title2 = path, art = R(ART))
	catscrape = JSON.ObjectFromURL(VIDEOS_PAGE%(Prefs['lang'],)+"plus7.json")
	for category in catscrape['videos']:
		if path in category['video_channels'].split(', '):
			sum=category['airdate_long'].capitalize() + '.\n' + category['desc'] + 'Categories : ' + category['video_channels'] + '. Durée : ' + str(category['duration']) + ' min.'
			if(Prefs['lang']=="de"):
				vid = JSON.ObjectFromURL("http://arte.tv/papi/tvguide/videos/stream/player/D/" + category['em'] +"_PLUS7-D/ALL/ALL.json")
			else:
				vid = JSON.ObjectFromURL("http://arte.tv/papi/tvguide/videos/stream/player/F/" + category['em'] +"_PLUS7-F/ALL/ALL.json")
			rating_key = '%s%s'
			dir.add(
				VideoClipObject(
					key = Callback(Lookup, title=vid["videoJsonPlayer"]["VTI"], rating_key=rating_key, url=vid["videoJsonPlayer"]["VSR"]["HTTP_MP4_SQ_1"]["url"], url2=vid["videoJsonPlayer"]["VSR"]["HTTP_MP4_MQ_1"]["url"], thum=category['image_url'], sum=sum),
					url = vid["videoJsonPlayer"]["VSR"]["HTTP_MP4_SQ_1"]["url"],
					title = vid["videoJsonPlayer"]["VTI"],
					thumb = Resource.ContentsOfURLWithFallback(url=category['image_url'], fallback="icon-default.png"),
					summary = sum,
					items = [
						MediaObject(
						video_resolution = 720,
						video_codec = "H264",
						container = "mp4",
						parts = [PartObject(key=Callback(PlayVideo, url=vid["videoJsonPlayer"]["VSR"]["HTTP_MP4_SQ_1"]["url"]))]                
						),MediaObject(
						video_resolution = 480,
						video_codec = "H264",
						container = "mp4",
						parts = [PartObject(key=Callback(PlayVideo, url=vid["videoJsonPlayer"]["VSR"]["HTTP_MP4_MQ_1"]["url"]))]                
						)
					]
				)
			)

	return dir

def PlayVideo(url):
	 return Redirect(url)

def Lookup(title, rating_key, url, url2, thum, sum):
	oc = ObjectContainer()
	oc.add(
		VideoClipObject(
			key = Callback(Lookup, title=title, rating_key=rating_key, url=url, url2=url2, thum=thum, sum=sum),
			title = title,
			rating_key = rating_key,
			thumb = Resource.ContentsOfURLWithFallback(url=thum, fallback="icon-default.png"),
			summary = sum,
			items = [
				MediaObject(
					video_resolution = 720,
					video_codec = "H264",
					container = "mp4",
					parts = [PartObject(key=Callback(PlayVideo, url=url))]
				),
				MediaObject(
					video_resolution = 480,
					video_codec = "H264",
					container = "mp4",
					parts = [PartObject(key=Callback(PlayVideo, url=url2))]
				)
			]
		)
	)
	return oc
