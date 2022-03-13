
import os
from pathlib import Path
import urllib.parse as up

# Const variables

## # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
##                                           COMMON                                            #
## # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

ROOT_PATH = Path(os.path.abspath(__file__)).parent.parent.absolute()
LOG_PATH = str(ROOT_PATH) + os.sep + "log"
LOG_HEADER = "="*50+"\n\tExecution Log File\n\tCreation Date : %s\n"+"="*50+"\n\n"
LOG_HEADER_DATE_FORMAT = "%Y %m %d - %H:%M:%S"
LOG_FILE_DATE_FORMAT = "%Y%m%d_%H%M%S"
try:
    EMAIL_SUBJECT = os.environ["HDS_EMAIL_SUBJECT"]
except:
    EMAIL_SUBJECT = "Update Procedure"  # Default email subject
try:
    if os.getenv("HDS_MAX_VIDEOS_TO_FETCH").capitalize()=="None":
        MAX_VIDEOS_TO_FETCH = None
    else:
        MAX_VIDEOS_TO_FETCH = int(os.getenv("HDS_MAX_VIDEOS_TO_FETCH"))
except:
    MAX_VIDEOS_TO_FETCH = 5

## # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
##                                         WEB VARIABLES                                       #
## # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

YTB_API_KEY = os.environ['HDS_YOUTUBE_API_KEY']
YTB_HUGO_CHANNEL_URL = "https://www.youtube.com/c/HugoD%C3%A9crypte"


## # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
##                                      DATA BASE VARIABLES                                    #
## # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

# Data base file :
if os.getenv("HDS_USE_DB_LOCALHOST", "False").capitalize()=="True":
    choseLocalDatabase = str(input("Will use local database. Continue? y/n: ")).lower()
    assert choseLocalDatabase in ['yes', 'ye', 'y'], "Abort. Will not use local database"
    # --- used for local DB : -----
    DB_NAME = "HDSDB"
    DB_USER = "postgres"
    DB_PWD  = os.environ["PGSQL_LOCAL_PWD"]
    DB_HOST = "localhost"
else:
    # ----- for server DB : -----
    DB_CONN_STRING = os.environ["HDS_DBSERVER_CONN_STRING"]
    DB_NAME = up.urlparse(DB_CONN_STRING).path[1:]
    DB_USER = up.urlparse(DB_CONN_STRING).username
    DB_PWD  = up.urlparse(DB_CONN_STRING).password
    DB_HOST = up.urlparse(DB_CONN_STRING).hostname


# Default element stored into DB when no value :
DB_DEFAULT_VALUE = None

## # # # #     Video details table     # # # # #
##
## Structure :
##  - video_id      : [String] unique video ID given by youtube
##  - video_name    : [String] name of the youtube video (video title)
##  - video_date    : [Timestamp] release date of the video
##  - video_img     : [String] link to the video's picture
##  - video_desc    : [String] description associated to the video
##
class VIDEO_TABLE:
    NAME = "video_table"
    # Columns :
    COL_ID = "video_id"
    COL_NAME = "video_name"
    COL_DATE = "video_date"
    COL_IMG  = "video_img"
    COL_DESC = "video_desc"
    # variables :
    dicStructure = {COL_ID: "text",
                    COL_NAME: "text",
                    COL_DATE: "timestamp",
                    COL_IMG : "text",
                    COL_DESC: "text"}
    listKeys = [COL_ID]   # keys in order
    listColumns = list(dicStructure.keys())

## # # # #     Urls table     # # # # #
##
## Structure :
##  - url_full          : [String] full url
##  - url_short         : [String] first part of the full_url
##  - url_video_id      : [String] youtube video ID where this url was used
##
class URL_TABLE:
    NAME = "url_table"
    # Columns :
    COL_VIDEO_ID = "url_video_id"
    COL_URL_FULL = "url_full"
    COL_URL_SHORT = "url_short"
    # Variables :
    dicStructure = {COL_VIDEO_ID: "text",
                    COL_URL_FULL : "text",
                    COL_URL_SHORT: "text"}
    listKeys = [COL_VIDEO_ID, COL_URL_FULL]
    listColumns = list(dicStructure.keys())

## # # # #     Register table     # # # # #
##
## Structure :
##  - register_url_short        : [String] short url of the page (ex : 'www.ouest-france.fr' or 'www.actu.fr')
##  - register_common_name      : [String] common name of the media (In reality, we used the domain names. ex : 'ouest-france.fr' or 'actu.fr')
##
class REGISTER_TABLE:
    NAME = "register_table"
    # Columns :
    COL_URL_SHORT = "register_url_short"
    COL_COMMON_NAME = "register_common_name"
    # Variables :
    dicStructure = {COL_URL_SHORT: "text",
                    COL_COMMON_NAME: "text"}
    listKeys = [COL_URL_SHORT]
    listColumns = list(dicStructure.keys())

## # # # #     Youtube links table     # # # # #
##
## Structure :
##  - links_ytb_url         : [String] full youtube url
##  - links_ytb_channel     : [String] if it is a video link, name of the author channel
##  - links_ytb_msg         : [String] message of the link analysis
##
class LINKS_YTB_TABLE:
    NAME = "links_ytb_table"
    # Columns :
    COL_URL = "links_ytb_url"
    COL_CHANNEL = "links_ytb_channel"
    COL_MSG = "links_ytb_msg"
    # Variables :
    dicStructure = {COL_URL: "text",
                    COL_CHANNEL: "text",
                    COL_MSG: "text"}
    listKeys = [COL_URL]
    listColumns = list(dicStructure.keys())

## # # # #     Blacklist youtube channels table     # # # # #
##
## Structure :
##  - blacklist_ytb_channel_name        : [String] name of the channel blacklisted
##  - blacklist_ytb_channel_reason      : [String] reason why it is blacklisted (mandatory)
##
class BLACKLIST_YTB_CHANNEL_TABLE:
    NAME = "blacklist_ytb_channel_table"
    # Columns :
    COL_NAME = "blacklist_ytb_channel_name"
    COL_REASON = "blacklist_ytb_channel_reason"
    # Variables :
    dicStructure = {COL_NAME: "text",
                    COL_REASON: "text"}
    listKeys = [COL_NAME]
    listColumns = list(dicStructure.keys())

## # # # #     Blacklist table     # # # # #
##
## Structure :
##  - blacklist_url         : [String] short or full blacklisted url
##  - blacklist_reason      : [String] reason why it is blacklisted (mandatory)
##
class BLACKLIST_TABLE:
    NAME = "blacklist_table"
    # Columns :
    COL_URL = "blacklist_url"
    COL_REASON = "blacklist_reason"
    # Variables :
    dicStructure = {COL_URL: "text",
                    COL_REASON: "text"}
    listKeys = [COL_URL]
    listColumns = list(dicStructure.keys())

# List of all XXX_TABLE objects :
DB_LIST_TABLES_OBJ = [VIDEO_TABLE,
                      URL_TABLE,
                      REGISTER_TABLE,
                      LINKS_YTB_TABLE,
                      BLACKLIST_YTB_CHANNEL_TABLE,
                      BLACKLIST_TABLE]



## # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
##                            HARD ENCODED BLACKLISTED ELEMENTS                                #
## # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

# Structure is as follows : ((url, reason_of_blacklisting), (url, reason_of_blacklisting), ...)
LIST_BLACKLISTED_URL = (("radio-londres.fr", "This is and old domain name, owned by Hugo Travers, for one of the projects he made. It now redirects to his youtube home page account"),
                        ("twitch.tv", "So far, Hugo Decrypte never gave any 'twitch' link that is not a main page account url"),
                        ("www.twitch.tv", "So far, Hugo Decrypte never gave any 'twitch' link that is not a main page account url"),
                        ("m.twitch.tv", "So far, Hugo Decrypte never gave any 'twitch' link that is not a main page account url"),
                        ("m.me", "Messenger urls are not considered as a source"),
                        ("www.tipeee.com", "Tipeee urls are not considered as a source"),
                        ("soundcloud.com", "Soundcloud urls are not considered as a source"),
                        ("m.soundcloud.com", "Soundcloud urls are not considered as a source"),
                        ("open.spotify.com", "Spotify urls are not considered as a source"), # NEED TO BE IMPROVED : What if Hugo Decrypte gives a podcast's url on which he based his video ?
                        ("spoti.fi", "Spotify urls are not considered as a source"), # NEED TO BE IMPROVED : What if Hugo Decrypte gives a podcast's url on which he based his video ?
                        ("itunes.apple.com", "Itunes urls are not considered as a source"),  # NEED TO BE IMPROVED : What if Hugo Decrypte gives a podcast's url on which he based his video ?
                        ("https://apple.co/3aJ4VAq", "HugoDecrypte podcast"),
                        ("www.leohenry.fr", "Web site of one of HugoDecrypte's friends that is not a source"),
                        ("discord.gg", "Discord urls are not considered as a source"),
                        ("consent.yahoo.com", "Consent page. Not a source"),
                        ("play.google.com", "Google Play is not considered as a source"),
                        ("docs.google.com", "Google Docs is not considered as a source"),
                        ("drive.google.com", "Google Drive is not considered as a source"),
                        ("forms.gle", "Google Form is not considered as a source"),
                        ("https://www.brief.me/?coupon_token=offre_HUGODECRYPTE", "Ad. Not a source"),
                        ("Brief.me", "Ad. Not a source"),
                        ("https://nordvpn.org/hugodecrypte", "Ad. Not a source"),
                        ("http://timejump.me", "Texting app. Not a source"),
                        ("https://shows.acast.com/mashup-linterview", "HugoDecrypte podcasts"),
                        ("https://shows.acast.com/mashup-les-actus", "HugoDecrypte podcasts"),
                        ("https://www.tiktok.com/@hugodecrypte", "HugoDecrypte TikTok page"),
                        ("http://snapchat.com/add/clementlanot", "Not a source")
                        )

# Structure is as follows : ((channel_name, reason_of_blacklisting), (channel_name, reason_of_blacklisting), ...)
LIST_BLACKLISTED_YTB_CHANNEL = (("HugoDécrypte - Actus du jour", "Hugo Decrypte channel"),
                                ("HugoDécrypte", "Hugo Decrypte channel"),
                                ("Hugo Travers", "Channel owned by Hugo Travers"),
                                ("Craft", "Channel owned by Hugo Travers and Cyrus North"),
                                ("Mashup par HugoDécrypte", "Hugo Decrypte channel"))