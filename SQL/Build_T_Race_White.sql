USE tHUB
GO

/* clear constraints which cleans out the multi-primary key*/
DECLARE @database nvarchar(50)
DECLARE @table nvarchar(50)
SET @database = 'tHUB'
SET @table = 'ACS_T_Race_White'
DECLARE @sql nvarchar(255)
WHILE EXISTS(SELECT * FROM INFORMATION_SCHEMA.TABLE_CONSTRAINTS WHERE constraint_catalog = @database AND table_name = @table)
BEGIN
    SELECT  @sql = 'ALTER TABLE ' + @table + ' DROP CONSTRAINT ' + @table + '_pk' 
    FROM    INFORMATION_SCHEMA.TABLE_CONSTRAINTS 
    WHERE   constraint_catalog = @database AND 
            table_name = @table
    EXEC    sp_executesql @sql
END
GO
/* delete the table and build again */
IF OBJECT_ID ('ACS_T_Race_White', 'U') IS NOT NULL 
DROP TABLE ACS_T_Race_White
GO

CREATE TABLE ACS_T_Race_White
(
	geoid char(11) not null,
	acsyear int not null,
	white int,
	CONSTRAINT ACS_T_Race_White_pk primary key (geoid,acsyear)
)
GO

INSERT INTO ACS_T_Race_White
(
	geoid,acsyear,white
)
	SELECT
	SUBSTRING(GEOID,10,20),ACS5_END_YEAR,B01001H001_EST
	FROM _T_B01001H
GO