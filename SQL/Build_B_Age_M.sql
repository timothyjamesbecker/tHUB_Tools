USE tHUB
GO

/* clear constraints which cleans out the multi-primary key*/
DECLARE @database nvarchar(50)
DECLARE @table nvarchar(50)
SET @database = 'tHUB'
SET @table = 'B_Age_M'
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
IF OBJECT_ID ('B_Age_M', 'U') IS NOT NULL 
DROP TABLE B_Age_M
GO

CREATE TABLE B_Age_M
(
	geoid char(21) not null,
	acsyear int not null,
	median int,
	total int,
    between_0_and_5 int,
	between_5_and_9 int,
	between_10_and_14 int,
	between_15_and_17 int,
	between_18_and_64 int,
	between_65_and_66 int,
	between_67_and_69 int,
	between_70_and_74 int,
	between_75_and_79 int,
	between_80_and_84 int,
	between_85_and_up int,
	CONSTRAINT B_Age_M_pk primary key (geoid,acsyear)
)
GO

INSERT INTO B_Age_M 
(
	geoid,acsyear,median,total,between_0_and_5,between_5_and_9,between_10_and_14,between_15_and_17,
	between_18_and_64,between_65_and_66,between_67_and_69,between_70_and_74,between_75_and_79,
	between_80_and_84,between_85_and_up
)
	SELECT
	M.GEOID,
	M.ACS5_END_YEAR,
	U.B01002002_EST,
	M.B01001002_EST,
	M.B01001003_EST,
	M.B01001004_EST,
	M.B01001005_EST,
	M.B01001006_EST,
	(	(M.B01001002_EST)-
		(M.B01001003_EST+M.B01001004_EST+M.B01001005_EST+
		 M.B01001006_EST+M.B01001020_EST+M.B01001021_EST+
		 M.B01001022_EST+M.B01001023_EST+M.B01001024_EST+
	     M.B01001025_EST)
	),
	M.B01001020_EST,
	M.B01001021_EST,
	M.B01001022_EST,
	M.B01001023_EST,
	M.B01001024_EST,
	M.B01001025_EST
	FROM _B_B01001 AS M JOIN _B_B01002 AS U
		ON (M.GEOID = U.GEOID AND M.ACS5_END_YEAR = U.ACS5_END_YEAR)
GO