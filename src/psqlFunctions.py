# PostgreSQL mapped functions for easier use

import psycopg2
from typing_extensions import Literal


def getStructure(dicStructure, selection: Literal["all", "keys only", "values only"] = "all"):
    assert isinstance(dicStructure, dict), f"dicStructure should be a dict. Given : {dicStructure}"
    if selection=="all":
        text = "(" + ','.join([f"{key} {dicStructure[key]}" for key in dicStructure.keys()]) + ")"
    elif selection=="keys only":
        text = "(" + ','.join([key for key in dicStructure.keys()]) + ")"
    elif selection=="values only":
        # Special format with escaping "'" characters (replacing them by '\\u0027') :
        text = "(" + ','.join(["'" + dicStructure[key].replace("'", "\\u0027") + "'" for key in dicStructure.keys()]) + ")"
    return text


class DatabasePSQL(object):
    def __init__(self, database, user, password, **kwargs):
        self.database = database
        self.user = user
        self.password = password
        self.host = kwargs.get("host", '')
        self.port = kwargs.get("port", '')

    ##### database connection #####

    def createCursor(self):
        # url = up.urlparse(self.dbServerUrl)
        # connect = psycopg2.connect(database=url.path[1:], user=url.username, password=url.password, host=url.hostname, port=url.port)
        connect = psycopg2.connect(database=self.database, user=self.user, password=self.password,
                                   host=self.host, port=self.port)
        cursor = connect.cursor()
        return connect, cursor

    def closeCursor(self, connect, cursor):
        cursor.close()
        connect.close()

    ##### internal purpose methods #####

    def convertToDic(self, data, tableName):
        assert isinstance(data, (list, tuple)), f"parameter 'data' should be a list or a tuple. Given : {data}"
        assert len(data)!=0, "data list should not be empty"
        listColumns = self.getColumnsNames(tableName=tableName)
        assert len(data[0]) == len(listColumns), f"number of columns does not match number of elements in data's rows\n" \
                                                 f"Given number of columns : {len(listColumns)}\n" \
                                                 f"elements in a row : {len(data[0])}"
        dataList = []
        for row in data:
            dicTemp = {}
            for colName in listColumns:
                colType = self.getColumnType(tableName=tableName, colName=colName)
                colValue = row[listColumns.index(colName)]
                if colType == "text" and colValue != None:
                    dicTemp[colName] = colValue.replace("\\u0027", "'")  # unescaping "'" character
                else:
                    dicTemp[colName] = colValue
            dataList.append(dicTemp)
        return dataList

    def generateWhereKeysRequest(self, tableName, dicKeysValues):
        listTableKeys = self.getKeysNames(tableName)
        assert isinstance(dicKeysValues, dict) and len(dicKeysValues.keys()) >= 1, "Given keys 'dicKeysValues' must be a non-empty dict"
        for givenKey in dicKeysValues.keys(): assert givenKey in listTableKeys, f"Unknown given key : {givenKey}"
        whereRequest = f"{listTableKeys[0]}='{list(dicKeysValues.values())[0]}'"
        if len(list(dicKeysValues.values())) > 1:
            for i in range(1, len(list(dicKeysValues.values()))):
                whereRequest += f" AND {listTableKeys[i]}='{list(dicKeysValues.values())[i]}'"
        return whereRequest

    ##### generic purpose methods #####

    def clearDb(self):
        ## TO DO :
        ## Check if there is no faster way to do this
        for tableName in self.getTablesNames(): self.dropTable(tableName=tableName)

    def doQuery(self, query):
        connect, cursor = self.createCursor()
        cursor.execute(query)
        data = cursor.fetchall()
        self.closeCursor(connect, cursor)
        return data

    def existRow(self, tableName, dicKeysValues):
        return False if self.getRow(tableName=tableName, dicKeysValues=dicKeysValues) is None else True

    def isDataMissing(self, tableName, dicKeysValues, listColumnsToCheck):
        ## TO DO :
        ## Check if there is no faster way to do this
        assert isinstance(listColumnsToCheck, list) and len(listColumnsToCheck) > 0, f"'columnsToCheck' must be a non-empty list. Given : {listColumnsToCheck}"
        columnsInTable = self.getColumnsNames(tableName)
        for col in listColumnsToCheck: assert (col in columnsInTable), f"Unknown column name : {col}"
        dicRow = self.getRow(tableName=tableName, dicKeysValues=dicKeysValues)
        dbDefaultValue = None
        missing = False
        for key in dicRow.keys():
            if key in listColumnsToCheck and dicRow[key]==dbDefaultValue:
                missing = True
        return missing

    ##### getters #####

    def getTablesNames(self):
        connect, cursor = self.createCursor()
        cursor.execute("SELECT relname FROM pg_class WHERE relkind='r' AND relname !~ '^(pg_|sql_)'")
        data = cursor.fetchall()
        self.closeCursor(connect, cursor)
        return [dataTuple[0] for dataTuple in data]

    def getColumnsNames(self, tableName):
        # Columns are returned in their order of insertion into the table
        connect, cursor = self.createCursor()
        cursor.execute(f"SELECT * FROM {tableName}")
        desc = cursor.description
        self.closeCursor(connect, cursor)
        listColumns = [description[0] for description in desc]
        return listColumns

    def getColumnType(self, tableName, colName):
        connect, cursor = self.createCursor()
        cursor.execute(f"SELECT column_name, data_type FROM information_schema.columns "
                       f"WHERE table_name='{tableName}' AND column_name='{colName}'")
        data = cursor.fetchall()
        self.closeCursor(connect, cursor)
        return data[0][1]

    def getKeysNames(self, tableName):
        # source : https://wiki.postgresql.org/wiki/Retrieve_primary_key_columns
        connect, cursor = self.createCursor()
        cursor.execute(f"""SELECT a.attname, format_type(a.atttypid, a.atttypmod) AS data_type
                            FROM   pg_index i
                            JOIN   pg_attribute a ON a.attrelid = i.indrelid
                                                    AND a.attnum = ANY(i.indkey)
                            WHERE  i.indrelid = '{tableName}'::regclass
                            AND    i.indisprimary;""")
        data = cursor.fetchall()
        self.closeCursor(connect, cursor)
        return [element[0] for element in data]

    def getRow(self, tableName, dicKeysValues, convertToDic=True):
        whereKeysRequest = self.generateWhereKeysRequest(tableName=tableName, dicKeysValues=dicKeysValues)
        connect, cursor = self.createCursor()
        req = f"SELECT * FROM {tableName} WHERE {whereKeysRequest}"
        cursor.execute(req)
        data = cursor.fetchall()
        self.closeCursor(connect, cursor)
        # We assume that 'getRow' should return one unique item (or none) :
        assert len(data) <= 1, f"Too much elements returned by request (should return only 1) : {req}"
        if len(data) == 0:
            return None
        if convertToDic:
            listDic = self.convertToDic(data, tableName=tableName)
            return listDic[0]
        else:
            return data

    def getTableData(self, tableName, convertToDic=True):
        connect, cursor = self.createCursor()
        cursor.execute(f"SELECT * FROM {tableName}")
        data = cursor.fetchall()
        self.closeCursor(connect, cursor)
        if convertToDic and len(data)!=0:
            return self.convertToDic(data, tableName=tableName)
        else:
            return data

    def getKeyValues(self, tableName):
        listKeysNames = self.getKeysNames(tableName=tableName)
        assert len(listKeysNames)>0, f"No key defined for table '{tableName}'"
        selectRequest = listKeysNames[0]
        if len(listKeysNames)>1:
            for i in range(len(listKeysNames)): selectRequest+=f",{listKeysNames[i]}"
        connect, cursor = self.createCursor()
        cursor.execute(f"SELECT {selectRequest} FROM {tableName}")
        data = cursor.fetchall()
        self.closeCursor(connect, cursor)
        return data

    ##### adding methods #####

    def createTable(self, tableName, dicStructure, listKeys=None):
        if listKeys is None: listKeys = []
        assert isinstance(listKeys, (list, tuple)), f"keyLabels should be a list or a tuple. Given : {listKeys}"
        if not listKeys: primaryKeyString = ""
        else: primaryKeyString = f", PRIMARY KEY ({','.join(listKeys)})"
        connect, cursor = self.createCursor()
        cursor.execute(f"CREATE TABLE {tableName} {getStructure(dicStructure)[:-1]}{primaryKeyString})")
        connect.commit()
        self.closeCursor(connect, cursor)

    def insertInto(self, tableName, dicData):
        listColumns = self.getColumnsNames(tableName)
        for key in dicData.keys(): assert (key in listColumns), f"Unknown column name : {key}"
        # for col in listColumns: assert (col in dicData.keys()), f"ERROR missing column name : {col}"   # -> only to prevent inserting unfilled columns
        connect, cursor = self.createCursor()
        cursor.execute(f"INSERT INTO {tableName} {getStructure(dicData, 'keys only')} "
                       f"VALUES {getStructure(dicData, 'values only')}")
        connect.commit()
        self.closeCursor(connect, cursor)

    ##### modifying methods #####

    def updateData(self, tableName, dicKeysValues, dicData):
        listColumns = self.getColumnsNames(tableName)
        for key in dicData.keys(): assert (key in listColumns), f"Unknown column name : {key}"
        whereKeysRequest = self.generateWhereKeysRequest(tableName=tableName, dicKeysValues=dicKeysValues)
        data = []
        for key in dicData.keys(): data.append(key+"='"+dicData[key].replace("'", "\\u0027")+"'")
        # "\\u0027" is used to escape "'" character (in order to keep a PSQL correct syntax)
        data = ','.join(data)
        connect, cursor = self.createCursor()
        cursor.execute(f"UPDATE {tableName} SET {data} WHERE {whereKeysRequest}")
        connect.commit()
        self.closeCursor(connect, cursor)

    ##### deleting methods #####

    def dropTable(self, tableName):
        connect, cursor = self.createCursor()
        cursor.execute(f"DROP TABLE {tableName}")
        connect.commit()
        self.closeCursor(connect, cursor)

    def deleteRowFrom(self, tableName, dicKeysValues):
        whereKeysRequest = self.generateWhereKeysRequest(tableName=tableName, dicKeysValues=dicKeysValues)
        connect, cursor = self.createCursor()
        cursor.execute(f"DELETE FROM {tableName} WHERE {whereKeysRequest}")
        connect.commit()
        self.closeCursor(connect, cursor)
        assert self.existRow(tableName=tableName, dicKeysValues=dicKeysValues) is False, "Row has not been deleted"
