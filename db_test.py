import pyodbc as msdb

USER='tolstochenko_di'
PWD=123
HOST='192.168.2.42'
DB='z_AUTORU'

DRIVER=f"DRIVER={{SQL Server Native Client 11.0}};SERVER={HOST};DATABASE={DB};UID={USER};PWD={PWD}"

print(DRIVER)

try:
    with msdb.connect(DRIVER) as auto:
        auto.setdecoding(msdb.SQL_CHAR, encoding='utf-8')
        auto.setdecoding(msdb.SQL_WCHAR, encoding='utf-8')
        auto.setencoding(encoding='utf-8')
        
        print("Connected to {}".format(auto.getinfo(msdb.SQL_DATABASE_NAME)))
        query = "SELECT Title FROM Records"
        query_result = auto.execute(query).fetchval()
        
        if query_result:
            print(query_result)
    
except msdb.Error as er:
    print(er)
finally:
    if auto:
        auto.close()