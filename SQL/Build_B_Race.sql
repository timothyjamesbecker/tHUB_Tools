USE tHUB
GO

/* clear constraints which cleans out the multi-primary key*/
DECLARE @database nvarchar(50)
DECLARE @table nvarchar(50)
SET @database = 'tHUB'
SET @table = 'B_Race'
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
IF OBJECT_ID ('B_Race', 'U') IS NOT NULL 
DROP TABLE B_Race
GO

CREATE TABLE B_Race
(
	geoid char(21) not null,
	acsyear int not null,
	total int,
	white int,
	black int,
	native_american int,
	asian int,
	hawaiian_pacific int,
	other_single int,
	two_or_more int,
	two_with_other int,
	two_without_other int
	CONSTRAINT B_Race_pk primary key (geoid,acsyear)
)
GO

INSERT INTO B_Race
(
	geoid,acsyear,total,white,black,native_american,asian,hawaiian_pacific,
	other_single,two_or_more,two_with_other,two_without_other
)
	SELECT
	GEOID,ACS5_END_YEAR,B02001001_EST,B02001002_EST,B02001003_EST,B02001004_EST,B02001005_EST,
	B02001006_EST,B02001007_EST,B02001008_EST,B02001009_EST,B02001010_EST
	FROM _B_B02001
GO