USE tHUB
GO

/* clear constraints which cleans out the multi-primary key*/
DECLARE @database nvarchar(50)
DECLARE @table nvarchar(50)
SET @database = 'tHUB'
SET @table = 'ACS_T_Language'
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
IF OBJECT_ID ('ACS_T_Language', 'U') IS NOT NULL 
DROP TABLE ACS_T_Language
GO

CREATE TABLE ACS_T_Language
(
	geoid char(11) not null,
	acsyear int not null,
	total int,
	english_only int,
	english_not_well int,
	other_english_not_well int,
	CONSTRAINT ACS_T_Language_pk primary key (geoid,acsyear)
)
GO

USE tHUB
GO
INSERT INTO ACS_T_Language
(
	geoid, acsyear,total, english_only, english_not_well, other_english_not_well
)
	SELECT
	SUBSTRING(GEOID,10,20), ACS5_END_YEAR, B06007001_EST, B06007002_EST, B06007005_EST, B06007005_EST
	FROM _T_B06007
GO