#MSSQL Tester v 0.3, 10/07/2013-10/23/2013
#Timothy Becker, UCONN/SOE/CSE/Graduate Research Assistant
#MSSQL Connection Factory, wraps up sophisticated functionality in
#an easy to use extensible class...

import mssql

with mssql.MSSQL('{SQL Server}','arc-gis','tHUB') as my_mssql:
    
    #test creation
    sql = "IF OBJECT_ID('Test','U') is not null DROP TABLE Test"
    v = []
    my_mssql.query(sql,v,False)
    sql = "CREATE TABLE Test (test_id int primary key,test_value text)"
    v = []
    my_mssql.query(sql,v,False)

    #test insertion
    sql = "INSERT INTO Test VALUES(?,?)"
    v = [5,'Tim']
    my_mssql.query(sql,v,False)
    sql = "INSERT INTO Test VALUES(?,?)"
    v = [6,'Donald']
    my_mssql.query(sql,v,False)

    #test deletion
    sql = "DELETE FROM Test WHERE test_id = ?"
    v = [6]
    my_mssql.query(sql,v,False)
    
    #test query, should only return Tim
    sql = "SELECT * FROM Test"
    v = []
    response = my_mssql.query(sql,v,True)
    for r in response: print(r)

    #delete and finish tests
    sql = "IF OBJECT_ID('Test','U') is not null DROP TABLE Test"
    v = []
    my_mssql.query(sql,v,False)

