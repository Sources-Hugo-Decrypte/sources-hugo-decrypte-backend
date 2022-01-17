
import os
import pafy
import scrapetube
from const import *

def youtubeGetUrlFromVideoId(videoId):
    return "https://www.youtube.com/watch?v=%s" % videoId

def youtubeExtractDetails(url):
    video = pafy.new(url)
    return {VIDEO_TABLE.COL_DATE: video.published.replace('Z',''),
            VIDEO_TABLE.COL_NAME: video.title,
            VIDEO_TABLE.COL_IMG : video.bigthumb,
            VIDEO_TABLE.COL_DESC: video.description}

# def youtubeExtractSingleVideoDescription(url):
#     video = pafy.new(url, private_api_key=YOUTUBE_API_KEY)
#     return video.description

def youtubeGetAllVideosFromUserChannel(url, limit=None):
    videosGeneratorObject = scrapetube.get_channel(channel_url=url, limit=limit)
    videosUrl = []
    for video in videosGeneratorObject: videosUrl.append(video['videoId'])
    return videosUrl
