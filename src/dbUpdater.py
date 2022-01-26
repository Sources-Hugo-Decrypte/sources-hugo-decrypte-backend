
import logging
from psqlFunctions import *
from youtubeFunctions import *
from const import *
from webRequestFunctions import checkUrl
from urlTextTreatment import *


class DatabaseUpdater(object):
    def __init__(self, database, user, password, logger, **kwargs):
        if logger is None: logger=logging
        self.logger = logger
        host = kwargs.get("host", '')
        port = kwargs.get("port", '')
        self.db = DatabasePSQL(database=database, user=user, password=password, host=host, port=port)

    def createTablesIntoDb(self):
        for objTable in DB_LIST_TABLES_OBJ:
            try:
                self.db.createTable(tableName=objTable.NAME, dicStructure=objTable.dicStructure, listKeys=objTable.listKeys)
                self.logger.info(f"New table added into db : {objTable.NAME}")
            except Exception:
                self.logger.exception(f"Unable to add table '{objTable.NAME}' into db")

    ########## generic purpose methods ##########

    def getListKnownVideoId(self):
        listKnownVideoId = self.db.getKeyValues(tableName=VIDEO_TABLE.NAME)
        listKnownVideoId = [listKnownVideoId[i][0] for i in range(len(listKnownVideoId))]  # transform result into list
        return listKnownVideoId

    def addUrlToBlacklist(self, url, reason):
        assert isinstance(url, str), f"'url' should be a string. Given : {type(url)}"
        assert isinstance(reason, str), f"'reason' should be a string. Given : {type(reason)}"
        assert len(reason)!=0, "'reason' should not be empty"
        # Ensure that this url exists (to only save meaningful urls):
        queryResult = self.db.doQuery(f"SELECT * FROM {URL_TABLE.NAME} "
                                      f"WHERE {URL_TABLE.COL_URL_FULL}='{url}' "
                                      f"OR {URL_TABLE.COL_URL_SHORT}='{url}'")
        assert len(queryResult)!=0, f"The given url doesn't exist in '{URL_TABLE.NAME}'. Given : '{url}'"
        self.db.insertInto(tableName=BLACKLIST_TABLE.NAME, dicData={BLACKLIST_TABLE.COL_URL: url,
                                                                    BLACKLIST_TABLE.COL_REASON: reason})

    ########## DB update procedure methods ##########

    def step01_generic_checkNewVideos(self, limit, logEn=True):
        ##### Add line to try internet connection #####
        assert isinstance(limit, int) or limit is None, f"'limit' should be either 'None' or an int. Given : {limit}"
        listVideoId = youtubeGetAllVideosFromUserChannel(YTB_HUGO_CHANNEL_URL, limit=limit)
        # Ensure that there are no duplicates in the returned video Ids :
        assert len(listVideoId) == len(set(listVideoId)), "Duplicates ids found"
        listKnownVideoId = self.getListKnownVideoId()
        toDelete = []
        for videoId in listVideoId:
            if videoId in listKnownVideoId:
                toDelete.append(videoId)
        for videoId in toDelete: listVideoId.remove(videoId)
        if logEn:
            if len(listVideoId) == 0:
                self.logger.info("No new video to add to database")
            else:
                self.logger.info(f"New video found total : {len(listVideoId)}")
            for videoId in listVideoId: self.logger.info(f"New video found : {videoId}")
        return listVideoId

    def step11_videoTable_createRowsFromListVideoId(self, listVideoId, logEn=True):
        for videoId in listVideoId:
            try:
                self.db.insertInto(tableName=VIDEO_TABLE.NAME, dicData={VIDEO_TABLE.COL_ID: videoId})
                if logEn: self.logger.info(f"Video id added into DB. Id '{videoId}'")
            except Exception as e:
                # self.logger.exception(f"Error occurred with id {videoId}")
                self.logger.error(f"Error occurred with video id '{videoId}'\n{e}")

    def step12_videoTable_addVideoDetails(self, listVideoId, overwrite=False, doAll=False, logEn=True):
        ##### Add line to try internet connection #####
        if not doAll: assert isinstance(listVideoId, list), f"'listVideoId should be a list. Given {listVideoId}"
        else: listVideoId = self.getListKnownVideoId()
        for videoId in listVideoId:
            try:
                if overwrite or self.db.isDataMissing(tableName=VIDEO_TABLE.NAME,
                                                      dicKeysValues={VIDEO_TABLE.COL_ID: videoId},
                                                      listColumnsToCheck=VIDEO_TABLE.listColumns):
                    dicDetails = youtubeExtractDetails(youtubeGetUrlFromVideoId(videoId))
                    self.db.updateData(tableName=VIDEO_TABLE.NAME,
                                       dicKeysValues={VIDEO_TABLE.COL_ID: videoId},
                                       dicData={VIDEO_TABLE.COL_NAME: dicDetails.get(VIDEO_TABLE.COL_NAME, DB_DEFAULT_VALUE),
                                                VIDEO_TABLE.COL_DATE: dicDetails.get(VIDEO_TABLE.COL_DATE, DB_DEFAULT_VALUE),
                                                VIDEO_TABLE.COL_DESC: dicDetails.get(VIDEO_TABLE.COL_DESC, DB_DEFAULT_VALUE),
                                                VIDEO_TABLE.COL_IMG : dicDetails.get(VIDEO_TABLE.COL_IMG, DB_DEFAULT_VALUE)})
                    if logEn: self.logger.info(f"Details modified. Video id '{videoId}'")
            except Exception as e:
                # self.logger.exception(f"Error occurred with video id '{videoId}'")
                self.logger.error(f"Error occurred with video id '{videoId}'\n{e}")

    def step21_urlTable_createRowsFromListVideoId(self, listVideoId, doAll=False, logEn=True):
        if not doAll: assert isinstance(listVideoId, list), f"'listVideoId should be a list. Given {listVideoId}"
        else: listVideoId = self.getListKnownVideoId()
        for videoId in listVideoId:
            try:
                dicVideoDetails = self.db.getRow(tableName=VIDEO_TABLE.NAME, dicKeysValues={VIDEO_TABLE.COL_ID: videoId})
                assert dicVideoDetails[VIDEO_TABLE.COL_DESC] not in [DB_DEFAULT_VALUE, ''], f"No description for video id '{videoId}'"
                listUrl = getAllUrlsFromDescription(dicVideoDetails[VIDEO_TABLE.COL_DESC])
                for url in listUrl:
                    try:
                        shortUrl = getShortUrl(url)
                        self.db.insertInto(tableName=URL_TABLE.NAME, dicData={URL_TABLE.COL_VIDEO_ID: videoId,
                                                                              URL_TABLE.COL_URL_FULL: url,
                                                                              URL_TABLE.COL_URL_SHORT: shortUrl})
                        if logEn: self.logger.info(f"New url added. Video id '{videoId}'. Url '{url}'")
                    except Exception as e:
                        # if logEn: self.logger.exception(f"Error occurred with video id '{videoId}'")
                        self.logger.error(f"Error occurred with video id '{videoId}' and url '{url}'\n{e}")
            except Exception as e:
                self.logger.error(f"Error occurred with video id '{videoId}'\n{e}")

    def step22_urlTable_addCheck(self, listVideoId, overwrite=False, doAll=False, logEn=True):
        if not doAll: assert isinstance(listVideoId, list), f"'listVideoId should be a list. Given {listVideoId}"
        else: listVideoId = self.getListKnownVideoId()
        for videoId in listVideoId:
            try:
                listUrl = self.db.doQuery(f"SELECT {URL_TABLE.COL_URL_FULL} FROM {URL_TABLE.NAME} "
                                          f"WHERE {URL_TABLE.COL_VIDEO_ID}='{videoId}'")
                assert len(listUrl)!=0, f"No url known for video id '{videoId}'"
                listUrl = [listUrl[i][0] for i in range(len(listUrl))]
                for url in listUrl:
                    try:
                        if overwrite or self.db.isDataMissing(tableName=URL_TABLE.NAME,
                                                              dicKeysValues={URL_TABLE.COL_VIDEO_ID: videoId,
                                                                             URL_TABLE.COL_URL_FULL: url},
                                                              listColumnsToCheck=[URL_TABLE.COL_CHECK_STATUS,
                                                                                  URL_TABLE.COL_CHECK_MSG]):
                            checkStatus, checkMsg = checkUrl(url)
                            self.db.updateData(tableName=URL_TABLE.NAME,
                                               dicKeysValues={URL_TABLE.COL_VIDEO_ID: videoId,
                                                              URL_TABLE.COL_URL_FULL: url},
                                               dicData={URL_TABLE.COL_CHECK_STATUS: checkStatus,
                                                        URL_TABLE.COL_CHECK_MSG: checkMsg})
                            if logEn:
                                self.logger.info(f"Url checked. Video id '{videoId}'. Url : '{url}'")
                                if checkStatus.upper()!="OK":
                                    self.logger.warning(f"Check status not OK. Check message : {checkMsg}. Video id '{videoId}'. Url : '{url}'")
                    except Exception as e:
                        self.logger.error(f"Error occurred with video id '{videoId}' and url '{url}'\n{e}")
            except Exception as e:
                self.logger.error(f"Error occurred with video id '{videoId}'\n{e}")

    def step31_registerTable_updateTable(self, logEn=True):
        listShortUrl = self.db.doQuery(f"SELECT DISTINCT {URL_TABLE.COL_URL_SHORT} FROM {URL_TABLE.NAME}")
        if len(listShortUrl)>0: listShortUrl = [listShortUrl[i][0] for i in range(len(listShortUrl))]
        listShortUrlKnown = self.db.getKeyValues(tableName=REGISTER_TABLE.NAME)
        if len(listShortUrlKnown)>0: listShortUrlKnown = [listShortUrlKnown[i][0] for i in range(len(listShortUrlKnown))]
        for shortUrl in listShortUrl:
            try:
                if shortUrl not in listShortUrlKnown:
                    domainUrl = getDomainUrl(shortUrl)
                    self.db.insertInto(tableName=REGISTER_TABLE.NAME, dicData={REGISTER_TABLE.COL_URL_SHORT: shortUrl,
                                                                               REGISTER_TABLE.COL_COMMON_NAME: domainUrl})
                    if logEn: self.logger.info(f"New short url '{shortUrl}'. Domain url : '{domainUrl}'")
            except Exception:
                self.logger.exception(f"Error occurred with short url '{shortUrl}'")
        if logEn: self.logger.info("Update done")

    def step41_links_updateLinksYtbTable(self, logEn=True):
        listYoutubeSpecificShortUrl = ('youtube.com', 'www.youtube.com', 'm.youtube.com', 'gaming.youtube.com', 'youtu.be', 'www.youtu.be', 'yt.be')
        whereRequest = f"{URL_TABLE.COL_URL_SHORT}='{listYoutubeSpecificShortUrl[0]}'"
        for i in range(1, len(listYoutubeSpecificShortUrl)):
            whereRequest += f"OR {URL_TABLE.COL_URL_SHORT}='{listYoutubeSpecificShortUrl[i]}'"
        # Extract links from DB :
        queryResult = self.db.doQuery(f"SELECT DISTINCT {URL_TABLE.COL_URL_FULL} FROM {URL_TABLE.NAME} "
                                      f"WHERE {whereRequest}")
        listLinks = [queryResult[i][0] for i in range(len(queryResult))]
        listLinksKnown = self.db.getKeyValues(tableName=LINKS_YTB_TABLE.NAME)
        if len(listLinksKnown)>0: listLinksKnown = [listLinksKnown[i][0] for i in range(len(listLinksKnown))]
        # Analyse links :
        for link in listLinks:
            if link not in listLinksKnown:
                try:
                    channelName = pafy.new(link, private_api_key=YTB_API_KEY).author
                    self.db.insertInto(tableName=LINKS_YTB_TABLE.NAME, dicData={LINKS_YTB_TABLE.COL_URL: link,
                                                                                LINKS_YTB_TABLE.COL_CHANNEL: channelName,
                                                                                LINKS_YTB_TABLE.COL_MSG: "OK"})
                    if logEn: self.logger.info(f"Analysis OK. New video : '{link}'")
                except Exception as e:
                    try:
                        self.db.insertInto(tableName=LINKS_YTB_TABLE.NAME, dicData={LINKS_YTB_TABLE.COL_URL: link,
                                                                                    LINKS_YTB_TABLE.COL_CHANNEL: "NOT_FOUND",
                                                                                    LINKS_YTB_TABLE.COL_MSG: str(e)})
                        if logEn: self.logger.info(f"Analysis OK. Not a video : '{link}'")
                    except Exception:
                        self.logger.exception(f"Error with link '{link}'")
        if logEn: self.logger.info("Update done")

    def step81_blacklistTable_updateTable(self, logEn=True):
        listBlacklistedUrlsKnown = self.db.getKeyValues(tableName=BLACKLIST_TABLE.NAME)
        if len(listBlacklistedUrlsKnown)>0 : listBlacklistedUrlsKnown = [listBlacklistedUrlsKnown[i][0] for i in range(len(listBlacklistedUrlsKnown))]
        ##### Blacklisting based on ytb link analysis : #####
        queryResult = self.db.doQuery(f"SELECT * FROM {LINKS_YTB_TABLE.NAME} "
                                      f"WHERE NOT {LINKS_YTB_TABLE.COL_MSG}='OK'")
        listColumnsLinksYtbTable = self.db.getColumnsNames(tableName=LINKS_YTB_TABLE.NAME)
        for element in queryResult:
            link = element[listColumnsLinksYtbTable.index(LINKS_YTB_TABLE.COL_URL)]
            if link not in listBlacklistedUrlsKnown:
                try:
                    reason = "Ytb link analysis | " + element[listColumnsLinksYtbTable.index(LINKS_YTB_TABLE.COL_MSG)]
                    self.db.insertInto(tableName=BLACKLIST_TABLE.NAME, dicData={BLACKLIST_TABLE.COL_URL: link,
                                                                                BLACKLIST_TABLE.COL_REASON: reason})
                    if logEn: self.logger.info(f"Ytb link blacklisted : '{link}'. Reason : '{reason}'")
                except Exception:
                    self.logger.exception(f"Error occurred with link : '{link}'")
        ##### Blacklisting based on ytb channels : #####
        queryResult = self.db.doQuery(f"SELECT {LINKS_YTB_TABLE.COL_URL},{LINKS_YTB_TABLE.COL_CHANNEL},{BLACKLIST_YTB_CHANNEL_TABLE.COL_REASON} "
                                      f"FROM {LINKS_YTB_TABLE.NAME} INNER JOIN {BLACKLIST_YTB_CHANNEL_TABLE.NAME} "
                                      f"ON {LINKS_YTB_TABLE.COL_CHANNEL}={BLACKLIST_YTB_CHANNEL_TABLE.COL_NAME}")
        for element in queryResult:
            link = element[0]
            if link not in listBlacklistedUrlsKnown:
                try:
                    reason = "Ytb channel blacklisted | " + element[2]
                    self.db.insertInto(tableName=BLACKLIST_TABLE.NAME, dicData={BLACKLIST_TABLE.COL_URL: link,
                                                                                BLACKLIST_TABLE.COL_REASON: reason})
                    if logEn: self.logger.info(f"Ytb link blacklisted : '{link}'. Reason : '{reason}'")
                except Exception:
                    self.logger.exception(f"Error occurred with link : '{link}'")
        ##### Blacklisting 'instagram' urls : #####
        ##### Caution : so far we don't check if a post was published by HugoDecrypte (and if so, we should blacklist it)
        queryResult = self.db.doQuery(f"SELECT DISTINCT {URL_TABLE.COL_URL_FULL} FROM {URL_TABLE.NAME} "
                                      f"INNER JOIN {REGISTER_TABLE.NAME} ON {URL_TABLE.COL_URL_SHORT}={REGISTER_TABLE.COL_URL_SHORT} "
                                      f"WHERE {REGISTER_TABLE.COL_COMMON_NAME} LIKE '%instagram%' "
                                      f"AND NOT {URL_TABLE.COL_URL_FULL} LIKE '%/p/%'")
        for element in queryResult:
            link = element[0]
            if link not in listBlacklistedUrlsKnown:
                try:
                    reason = "Not an instagram post"
                    self.db.insertInto(tableName=BLACKLIST_TABLE.NAME, dicData={BLACKLIST_TABLE.COL_URL: link,
                                                                                BLACKLIST_TABLE.COL_REASON: reason})
                    if logEn: self.logger.info(f"Insta link blacklisted : '{link}'. Reason : '{reason}'")
                except Exception:
                    self.logger.exception(f"Error occurred with link : '{link}'")
        ##### Blacklisting 'twitter' urls : #####
        queryResult = self.db.doQuery(f"SELECT DISTINCT {URL_TABLE.COL_URL_FULL} FROM {URL_TABLE.NAME} "
                                      f"INNER JOIN {REGISTER_TABLE.NAME} ON {URL_TABLE.COL_URL_SHORT}={REGISTER_TABLE.COL_URL_SHORT} "
                                      f"WHERE {REGISTER_TABLE.COL_COMMON_NAME} LIKE '%twitter%' "
                                      f"AND NOT {URL_TABLE.COL_URL_FULL} LIKE '%/status/%'")
        for element in queryResult:
            link = element[0]
            if link not in listBlacklistedUrlsKnown:
                try:
                    reason = "Not a twitter post"
                    self.db.insertInto(tableName=BLACKLIST_TABLE.NAME, dicData={BLACKLIST_TABLE.COL_URL: link,
                                                                                BLACKLIST_TABLE.COL_REASON: reason})
                    if logEn: self.logger.info(f"Twitter link blacklisted : '{link}'. Reason : '{reason}'")
                except Exception:
                    self.logger.exception(f"Error occurred with link : '{link}'")
        ##### Blacklisting 'HugoTravers' twitter publications : #####
        queryResult = self.db.doQuery(f"SELECT DISTINCT {URL_TABLE.COL_URL_FULL} FROM {URL_TABLE.NAME} "
                                      f"INNER JOIN {REGISTER_TABLE.NAME} ON {URL_TABLE.COL_URL_SHORT}={REGISTER_TABLE.COL_URL_SHORT} "
                                      f"WHERE {REGISTER_TABLE.COL_COMMON_NAME} LIKE '%twitter%' "
                                      f"AND {URL_TABLE.COL_URL_FULL} LIKE '%/status/%' "
                                      f"AND {URL_TABLE.COL_URL_FULL} LIKE '%/HugoTravers/%'")
        for element in queryResult:
            link = element[0]
            if link not in listBlacklistedUrlsKnown:
                try:
                    reason = "Twitter publication posted by HugoTravers"
                    self.db.insertInto(tableName=BLACKLIST_TABLE.NAME, dicData={BLACKLIST_TABLE.COL_URL: link,
                                                                                BLACKLIST_TABLE.COL_REASON: reason})
                    if logEn: self.logger.info(f"Twitter link blacklisted : '{link}'. Reason : '{reason}'")
                except Exception:
                    self.logger.exception(f"Error occurred with link : '{link}'")
        ##### Blacklisting 'facebook' links : #####
        queryResult = self.db.doQuery(f"SELECT DISTINCT {URL_TABLE.COL_URL_FULL} FROM {URL_TABLE.NAME} "
                                      f"INNER JOIN {REGISTER_TABLE.NAME} ON {URL_TABLE.COL_URL_SHORT}={REGISTER_TABLE.COL_URL_SHORT} "
                                      f"WHERE {REGISTER_TABLE.COL_COMMON_NAME} LIKE '%facebook%' "
                                      f"AND NOT ({URL_TABLE.COL_URL_FULL} LIKE '%/posts/%' "
                                                f"OR {URL_TABLE.COL_URL_FULL} LIKE '%/videos/%' "
                                                f"OR {URL_TABLE.COL_URL_FULL} LIKE '%/events/%')")
        for element in queryResult:
            link = element[0]
            if link not in listBlacklistedUrlsKnown:
                try:
                    reason = "Not a facebook publication"
                    self.db.insertInto(tableName=BLACKLIST_TABLE.NAME, dicData={BLACKLIST_TABLE.COL_URL: link,
                                                                                BLACKLIST_TABLE.COL_REASON: reason})
                    if logEn: self.logger.info(f"Facebook link blacklisted : '{link}'. Reason : '{reason}'")
                except Exception:
                    self.logger.exception(f"Error occurred with link : '{link}'")

        if logEn: self.logger.info("Update done")


    ##### global procedures #####

    def dailyUpdate(self):
        self.logger.info("Start daily update procedure")
        listVideoId = self.step01_generic_checkNewVideos(limit=5)
        if len(listVideoId)!=0:
            self.step11_videoTable_createRowsFromListVideoId(listVideoId=listVideoId)
            self.step12_videoTable_addVideoDetails(listVideoId=listVideoId)
            self.step21_urlTable_createRowsFromListVideoId(listVideoId=listVideoId)
            # self.step22_urlTable_addCheck(listVideoId=listVideoId)
        self.step31_registerTable_updateTable()
        self.step41_links_updateLinksYtbTable()
        self.step81_blacklistTable_updateTable()
        self.logger.info("End of daily update procedure")





class DatabaseManualSettings(object):
    def __init__(self, database, user, password, logger, **kwargs):
        if logger is None: logger=logging
        self.logger = logger
        host = kwargs.get("host", '')
        port = kwargs.get("port", '')
        self.updater = DatabaseUpdater(logger=logging, database=database, user=user, password=password, host=host, port=port)

    ########## generic methods ##########

    def addToBlacklistedYtbChannel(self, channelName, reason):
        assert isinstance(channelName, str), f"'url' should be a string. Given : {type(channelName)}"
        assert isinstance(reason, str), f"'reason' should be a string. Given : {type(reason)}"
        assert len(reason) != 0, "'reason' should not be empty"
        # Ensure that this url channel name (to only save meaningful channel names):
        queryResult = self.updater.db.doQuery(f"SELECT * FROM {LINKS_YTB_TABLE.NAME} "
                                              f"WHERE {LINKS_YTB_TABLE.COL_CHANNEL}='{channelName}'")
        assert len(queryResult) != 0, f"The given channel name doesn't exist in '{LINKS_YTB_TABLE.NAME}'. Given : '{channelName}'"
        self.updater.db.insertInto(tableName=BLACKLIST_YTB_CHANNEL_TABLE.NAME,
                                   dicData={BLACKLIST_YTB_CHANNEL_TABLE.COL_NAME: channelName,
                                            BLACKLIST_YTB_CHANNEL_TABLE.COL_REASON: reason})

    ########## setting methods ##########

    def fillBlacklistTable(self, logEn=True):
        listBlacklistedUrlsKnown = self.updater.db.getKeyValues(tableName=BLACKLIST_TABLE.NAME)
        if len(listBlacklistedUrlsKnown) > 0: listBlacklistedUrlsKnown = [listBlacklistedUrlsKnown[i][0] for i in range(len(listBlacklistedUrlsKnown))]
        for element in LIST_BLACKLISTED_URL:
            if element[0] not in listBlacklistedUrlsKnown:
                try:
                    self.updater.addUrlToBlacklist(url=element[0], reason=element[1])
                    if logEn: self.logger.info(f"Element added to {BLACKLIST_TABLE.NAME}. Url : '{element[0]}'. Reason : '{element[1]}'")
                except Exception:
                    self.logger.exception(f"Error occurred with url '{element[0]}'")
        if logEn: self.logger.info("Filling done")

    def fillYtbChannelBlacklistTable(self, logEn=True):
        listBlacklistedChannelsKnown = self.updater.db.getKeyValues(tableName=BLACKLIST_YTB_CHANNEL_TABLE.NAME)
        if len(listBlacklistedChannelsKnown) > 0: listBlacklistedChannelsKnown = [listBlacklistedChannelsKnown[i][0] for i in range(len(listBlacklistedChannelsKnown))]
        for element in LIST_BLACKLISTED_YTB_CHANNEL:
            if element[0] not in listBlacklistedChannelsKnown:
                try:
                    self.addToBlacklistedYtbChannel(channelName=element[0], reason=element[1])
                    if logEn: self.logger.info(f"Element added to {BLACKLIST_YTB_CHANNEL_TABLE.NAME}. Channel : '{element[0]}'. Reason : '{element[1]}'")
                except Exception:
                    self.logger.exception(f"Error occurred with channel '{element[0]}'")
        if logEn: self.logger.info("Filling done")

    ########## main method ##########

    def update(self):
        # Update manual settings :
        self.fillBlacklistTable()
        self.fillYtbChannelBlacklistTable()
        # Update blacklist table :
        self.updater.step81_blacklistTable_updateTable()






