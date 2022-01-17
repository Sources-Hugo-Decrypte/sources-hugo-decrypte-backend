
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
                listUrl = getAllUrlsFromDescrption(dicVideoDetails[VIDEO_TABLE.COL_DESC])
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
                    self.db.insertInto(tableName=REGISTER_TABLE.NAME, dicData={REGISTER_TABLE.COL_URL_SHORT: shortUrl})
                    if logEn: self.logger.info(f"New short url '{shortUrl}'")
            except Exception:
                self.logger.exception(f"Error occurred with short url '{shortUrl}'")



    ##### global procedures #####

    def dailyUpdate(self):
        self.logger.info("Start daily update procedure")
        listVideoId = self.step01_generic_checkNewVideos(limit=3)
        if len(listVideoId)!=0:
            self.step11_videoTable_createRowsFromListVideoId(listVideoId=listVideoId)
            self.step12_videoTable_addVideoDetails(listVideoId=listVideoId)
            self.step21_urlTable_createRowsFromListVideoId(listVideoId=listVideoId)
            # self.step22_urlTable_addCheck(listVideoId=listVideoId)
            self.step31_registerTable_updateTable()
        self.logger.info("End of daily update procedure")






