
from datetime import datetime
from dbUpdater import *


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    print(ROOT_PATH)
    if 1:
        if not os.path.exists(LOG_PATH): os.mkdir(LOG_PATH)
        creationDate = datetime.now()
        fileLog = LOG_PATH + os.sep + creationDate.strftime("%Y%m%d_%H%M%S") + '.log'
        myLogger = logging.getLogger(__name__)
        for file in [fileLog]:
            with open(file, 'w') as f:
                f.write(LOG_HEADER % creationDate.strftime("%Y %m %d - %H:%M:%S"))
                f.close()
        # f_handler = logging.StreamHandler()
        f_handler = logging.FileHandler(filename=fileLog)
        f_handler.setLevel(logging.INFO)
        f_format = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(funcName)s - %(message)s')
        f_handler.setFormatter(f_format)
        myLogger.addHandler(f_handler)

    updater = DatabaseUpdater(logger=myLogger, database=DB_NAME, user=DB_USER, password=DB_PWD, host=DB_HOST)
    if 1:
        updater.db.clearDb()
        updater.createTablesIntoDb()
        updater.dailyUpdate()