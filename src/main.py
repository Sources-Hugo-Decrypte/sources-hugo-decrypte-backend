import atexit
from time import time
from datetime import datetime, timedelta
from dbUpdater import *
from emailFunctions import *

def emailProcedure():
    emailSubject = "HDS daily update"
    emailMessage = f"Program done. Find log in the attachment."
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
    if 1:
        if not os.path.exists(LOG_PATH): os.mkdir(LOG_PATH)
        creationDate = datetime.now()
        fileLog = LOG_PATH + os.sep + creationDate.strftime("%Y%m%d_%H%M%S") + '.log'
        fileLogError = LOG_PATH + os.sep + creationDate.strftime("%Y%m%d_%H%M%S") + '_error.log'
        myLogger = logging.getLogger(__name__)
        for file in [fileLog, fileLogError]:
            with open(file, 'w') as f:
                f.write(LOG_HEADER % creationDate.strftime("%Y %m %d - %H:%M:%S"))
                f.close()
        # f_handler = logging.StreamHandler()
        f_handler = logging.FileHandler(filename=fileLog)
        f_handler.setLevel(logging.INFO)
        f_format = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(funcName)s - %(message)s')
        f_handler.setFormatter(f_format)
        myLogger.addHandler(f_handler)
        # only error log file :
        fe_handler = logging.FileHandler(fileLogError)
        fe_handler.setLevel(logging.ERROR)
        fe_format = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(funcName)s - %(message)s')
        fe_handler.setFormatter(fe_format)
        myLogger.addHandler(fe_handler)

    updater = DatabaseUpdater(logger=myLogger, database=DB_NAME, user=DB_USER, password=DB_PWD, host=DB_HOST)
    if 0:
        updater.db.clearDb()
        updater.createTablesIntoDb()
    if 1:
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

