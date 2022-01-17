
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
##  - VIDEO_DATE    : [String] release date of the video
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
    listColumns = [COL_ID, COL_NAME, COL_DATE, COL_IMG, COL_DESC]    # columns in order
    listKeys = [COL_ID]   # keys in order
    dicStructure = {COL_ID: "text",
                    COL_NAME: "text",
                    COL_DATE: "timestamp",
                    COL_IMG : "text",
                    COL_DESC: "text"}

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
    listColumns = [COL_VIDEO_ID, COL_URL_FULL, COL_URL_SHORT, COL_CHECK_STATUS, COL_CHECK_MSG]
    listKeys = [COL_VIDEO_ID, COL_URL_FULL]
    dicStructure = {COL_VIDEO_ID: "text",
                    COL_URL_FULL : "text",
                    COL_URL_SHORT: "text",
                    COL_CHECK_STATUS: "text",
                    COL_CHECK_MSG: "text"}


## # # # #     Register table     # # # # #
##
## Structure :
##  - REGISTER_SHORT_URL    : [String] short url of the page (ex : 'www.ouest-france.fr' or 'actu.fr')
##  - REGISTER_NAME         : [String] common name of the media (ex : 'Ouest-France' or 'Actu')
class REGISTER_TABLE:
    NAME = "register_table"
    # Columns :
    COL_URL_SHORT = "register_url_short"
    COL_COMMON_NAME = "register_common_name"
    # Variables :
    listColumns = [COL_URL_SHORT, COL_COMMON_NAME]
    listKeys = [COL_URL_SHORT]
    dicStructure = {COL_URL_SHORT: "text",
                    COL_COMMON_NAME: "text"}


# List of all XXX_TABLE objects :
DB_LIST_TABLES_OBJ = [VIDEO_TABLE, URL_TABLE, REGISTER_TABLE]

