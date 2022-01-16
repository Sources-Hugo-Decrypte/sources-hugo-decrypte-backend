
##
## TO DO :
## Remove following columns in db :
##  - short url
##  - video id
##  - number of uses (?)
##


import json
import os
import pafy
import timing
from manageDB import *

def linksAnalysisYoutube():
    listYoutubeSpecificShortUrl = ('youtube.com', 'www.youtube.com', 'm.youtube.com', 'gaming.youtube.com', 'youtu.be', 'www.youtu.be')
    ##### EXTRACTION FROM DB #####
    listAllLinks = []
    for stringShortUrl in listYoutubeSpecificShortUrl:
        queryResult = dbUrlTable.doQuery(
            f'SELECT DISTINCT {URL_SHORT}, {URL_FULL} FROM {URL_TABLE_NAME} WHERE {URL_SHORT}="{stringShortUrl}"')
        for el in queryResult:
            # only add if not already in table:
            if el[1] not in getAllYoutubeTableKeys():
                listAllLinks.append({YOUTUBE_URL_SHORT: el[0],
                                   YOUTUBE_URL_FULL: el[1]})
    # Add more details :
    for dic in listAllLinks:
        queryRes = dbUrlTable.doQuery(f'SELECT COUNT(*) FROM {URL_TABLE_NAME} WHERE {URL_FULL}="{dic[YOUTUBE_URL_FULL]}"')
        dic[YOUTUBE_NUMBER_OF_USES] = queryRes[0][0]
    for dic in listAllLinks:
        queryRes = dbUrlTable.doQuery(f'SELECT {URL_VIDEO_ID} FROM {URL_TABLE_NAME} WHERE {URL_FULL}="{dic[YOUTUBE_URL_FULL]}"')
        dic[YOUTUBE_MAIN_VIDEO_ID] = queryRes[0][0]
    ##### DEFINE IF IT'S A SOURCE OR NOT #####
    count = 1
    for dic in listAllLinks:
        print(f"Element {count}/{len(listAllLinks)}")
        try:
            channelName = pafy.new(dic[YOUTUBE_URL_FULL], private_api_key=YOUTUBE_API_KEY).author
            dic[YOUTUBE_CHANNEL_NAME] = channelName
            dic[YOUTUBE_LINK_CONSIDERED_AS_VIDEO] = "YES"
            dic[YOUTUBE_ANALYSIS_MSG] = "OK"
            print("Accepted")
        except Exception as e:
            dic[YOUTUBE_CHANNEL_NAME] = "NOT_FOUND"
            dic[YOUTUBE_LINK_CONSIDERED_AS_VIDEO] = "NO"
            dic[YOUTUBE_ANALYSIS_MSG] = str(e)
            print("Rejected ***")
        count += 1

    return listAllLinks

if __name__=='__main__':
    DB_LINKS_FILE = r"D:\Youen\Documents\Programmes\Programmes python\HugoDecrypteSources\db_video_sources_links.db"
    if not os.path.isfile(DB_LINKS_FILE): open(DB_LINKS_FILE, 'w').close()

    YOUTUBE_URL_FULL        = "YOUTUBE_URL_FULL"
    YOUTUBE_URL_SHORT       = "YOUTUBE_URL_SHORT"
    YOUTUBE_CHANNEL_NAME    = "YOUTUBE_CHANNEL_NAME"
    YOUTUBE_NUMBER_OF_USES  = "YOUTUBE_NUMBER_OF_USES"
    YOUTUBE_MAIN_VIDEO_ID   = "YOUTUBE_MAIN_VIDEO_ID"
    YOUTUBE_LINK_CONSIDERED_AS_VIDEO = "YOUTUBE_LINK_CONSIDERED_AS_VIDEO"
    YOUTUBE_ANALYSIS_MSG    = "YOUTUBE_ANALYSIS_MSG"
    ##
    YOUTUBE_TABLE_NAME = "YOUTUBE_TABLE_NAME"
    YOUTUBE_TABLE_COLUMNS = [YOUTUBE_URL_FULL, YOUTUBE_URL_SHORT, YOUTUBE_CHANNEL_NAME, YOUTUBE_NUMBER_OF_USES,
                             YOUTUBE_MAIN_VIDEO_ID, YOUTUBE_LINK_CONSIDERED_AS_VIDEO, YOUTUBE_ANALYSIS_MSG]
    YOUTUBE_TABLE_KEY = [YOUTUBE_URL_FULL]

    dbYoutubeTable = SQLTable(dbFile=DB_LINKS_FILE, tableName=YOUTUBE_TABLE_NAME, allLabels=YOUTUBE_TABLE_COLUMNS,
                            keyLabels=YOUTUBE_TABLE_KEY)

    def getAllYoutubeTableKeys():
        rqResult = dbYoutubeTable.doQuery(f"SELECT {YOUTUBE_URL_FULL} FROM {YOUTUBE_TABLE_NAME}")
        return [tuple[0] for tuple in rqResult]

    try:
        dbYoutubeTable.createTable()
    except:
        pass

    listData = linksAnalysisYoutube()
    numNew = 0
    for dicData in listData:
        if dicData[YOUTUBE_URL_FULL] not in getAllYoutubeTableKeys():
            dbYoutubeTable.createElement(dicData)
            print(f"New element added :\n{json.dumps(dicData, indent=2)}")
            numNew += 1
    print(f"Total : {numNew} elements added")
    print("Done")
