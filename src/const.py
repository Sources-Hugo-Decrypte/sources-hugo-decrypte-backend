
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


## # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
##                                         WEB VARIABLES                                       #
## # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

YTB_API_KEY = os.environ['HDS_YOUTUBE_API_KEY']
YTB_HUGO_CHANNEL_URL = "https://www.youtube.com/c/HugoD%C3%A9crypte"


## # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
##                                      DATA BASE VARIABLES                                    #
## # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

# Data base file :
# --- used for local DB : -----
# DB_NAME = "HDSDB"
# DB_USER = "postgres"
# DB_PWD  = os.environ["PGSQL_LOCAL_PWD"]
# DB_HOST = "localhost"
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
##  - VIDEO_ID      : [String] unique video ID given by youtube
##  - VIDEO_NAME    : [String] name of the youtube video (video title)
##  - VIDEO_DATE    : [Timestamp] release date of the video
##  - VIDEO_DESC    : [String] description associated to the video
##
class VIDEO_TABLE:
    NAME = "video_table"
    # Columns :
    COL_ID = "video_id"
    COL_NAME = "video_name"
    COL_DATE = "video_date"
    COL_DESC = "video_desc"
    COL_IMG  = "video_img"
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
##  - URL_FULL      : [String] full url
##  - URL_SHORT     : [String] first part of the full_url
##  - URL_VIDEO_ID  : [String] youtube video ID where this url was used
##  - URL_CHECK_MSG : [String] message returned when url has been checked
##
class URL_TABLE:
    NAME = "url_table"
    # Columns :
    COL_URL_SHORT = "url_short"
    COL_URL_FULL = "url_full"
    COL_VIDEO_ID = "url_video_id"
    COL_CHECK_STATUS = "url_check_status"
    COL_CHECK_MSG = "url_check_msg"
    # Variables :
    dicStructure = {COL_VIDEO_ID: "text",
                    COL_URL_FULL : "text",
                    COL_URL_SHORT: "text",
                    COL_CHECK_STATUS: "text",
                    COL_CHECK_MSG: "text"}
    listKeys = [COL_VIDEO_ID, COL_URL_FULL]
    listColumns = list(dicStructure.keys())

## # # # #     Register table     # # # # #
##
## Structure :
##  - REGISTER_SHORT_URL    : [String] short url of the page (ex : 'www.ouest-france.fr' or 'actu.fr')
##  - REGISTER_NAME         : [String] common name of the media (ex : 'Ouest-France' or 'Actu')
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
##  - LINKS_YOUTUBE_URL         : [String] full youtube url
##  - LINKS_YOUTUBE_CHANNEL     : [String] if it is a video link, name of the author channel
##  - LINKS_YOUTUBE_MSG         : [String] message of the link analysis
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
##  - BLACKLIST_YTB_CHANNEL_NAME        : [String] name of the channel blacklisted
##  - BLACKLIST_YTB_CHANNEL_REASON      : [String] reason why it is blacklisted (mandatory)
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
##  - BLACKLIST_URL         : [String] short or full blacklisted url
##  - BLACKLIST_REASON      : [String] reason why it is blacklisted (mandatory)
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
                        ("https://open.spotify.com/show/6y1PloEyNsCNJH9vHias4T?si=pz8U9CGkTCO_IGSEnMVxVw", "Hugo Decrypte's podcasts home page"))

# Structure is as follows : ((channel_name, reason_of_blacklisting), (channel_name, reason_of_blacklisting), ...)
LIST_BLACKLISTED_YTB_CHANNEL = (("HugoDécrypte - Actus du jour", "Hugo Decrypte channel"),
                                ("HugoDécrypte", "Hugo Decrypte channel"),
                                ("Hugo Travers", "Channel owned by Hugo Travers"),
                                ("Craft", "Channel owned bu Hugo Travers and Cyrus North"))