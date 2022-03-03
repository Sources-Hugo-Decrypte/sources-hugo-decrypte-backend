import atexit
import logging
from time import time
from datetime import datetime, timedelta
from dbUpdater import *
from emailFunctions import *

def logDataWithoutHeader(logFile):
    """
    Get data of log file without header
    """
    with open(logFile, 'r') as f:
        text = f.readlines()
        f.close()
    text = ''.join(text).replace(LOG_HEADER % creationDate.strftime(LOG_HEADER_DATE_FORMAT), '')
    return None if len(text)==0 else text


def emailProcedure():
    dataErrorLog = logDataWithoutHeader(fileLogError)
    if dataErrorLog is None:
        emailSubject = "Daily Routine | OK"
        emailMessage = f"Program done. Find log in the attachment."
        emailFiles = [fileLog]
    else:
        listLevels = [logging.NOTSET, logging.DEBUG, logging.INFO, logging.WARNING, logging.ERROR, logging.CRITICAL]
        majorLevel = levelLogError
        for level in listLevels[listLevels.index(majorLevel):]:
            if logging.getLevelName(level) in dataErrorLog and level>majorLevel: majorLevel=level
        emailSubject = f"Daily Routine | {logging.getLevelName(majorLevel)}"
        emailMessage = f"Program done. Errors occurred. Find logs in the attachment."
        emailFiles = [fileLog, fileLogError]
    send_mail(send_from="GitHub",
              send_to=[os.environ["HDS_GMAIL_ADDRESS"]],
              subject=emailSubject,
              message=emailMessage,
              files=emailFiles,
              server="smtp.gmail.com",
              username=os.environ["HDS_GMAIL_ADDRESS"],
              password=os.environ["HDS_GMAIL_APP_PASSWORD"])


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    if not os.path.exists(LOG_PATH): os.mkdir(LOG_PATH)
    creationDate = datetime.now()
    # ----- Globals -----
    fileLog = LOG_PATH + os.sep + creationDate.strftime(LOG_FILE_DATE_FORMAT) + '_log.txt'
    fileLogError = LOG_PATH + os.sep + creationDate.strftime(LOG_FILE_DATE_FORMAT) + '_error_log.txt'
    levelLogError = logging.WARNING
    # -------------------
    myLogger = logging.getLogger(__name__)
    for file in [fileLog, fileLogError]:
        with open(file, 'w') as f:
            f.write(LOG_HEADER % creationDate.strftime(LOG_HEADER_DATE_FORMAT))
            f.close()
    # f_handler = logging.StreamHandler()
    f_handler = logging.FileHandler(filename=fileLog)
    f_handler.setLevel(logging.INFO)
    f_format = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(funcName)s - %(message)s")
    f_handler.setFormatter(f_format)
    myLogger.addHandler(f_handler)
    # only error log file :
    fe_handler = logging.FileHandler(fileLogError)
    fe_handler.setLevel(levelLogError)
    fe_format = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(funcName)s - %(message)s")
    fe_handler.setFormatter(fe_format)
    myLogger.addHandler(fe_handler)

    MAX_VIDEOS_TO_FETCH = None # -> fetch every video published, without number limit

    updater = DatabaseUpdater(logger=myLogger, database=DB_NAME, user=DB_USER, password=DB_PWD, host=DB_HOST)
    try:
        atexit.register(emailProcedure) # Schedule sending email at end of execution
        timeStart = time()
        ### put below this line the tasks to execute ###
        updater.dailyUpdate()
        ### end of tasks to execute ###
        timeEnd = time()
        timeElapsed = timedelta(seconds=timeEnd-timeStart)
        myLogger.info(f"Program Done. Elapsed time {timeElapsed}")
    except Exception:
        myLogger.critical("Major Exception Occurred", exc_info=True)

