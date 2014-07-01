USE tHUB
GO

/* clear constraints which cleans out the multi-primary key*/
DECLARE @database nvarchar(50)
DECLARE @table nvarchar(50)
SET @database = 'tHUB'
SET @table = 'ACS_G_Age_F'
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
IF OBJECT_ID ('ACS_G_Age_F', 'U') IS NOT NULL 
DROP TABLE ACS_G_Age_F
GO

CREATE TABLE ACS_G_Age_F
(
	geoid char(12) not null,
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
	CONSTRAINT ACS_G_Age_F_pk primary key (geoid,acsyear)
)
GO

INSERT INTO ACS_G_Age_F 
(
	geoid,acsyear,median,total,between_0_and_5,between_5_and_9,between_10_and_14,between_15_and_17,
	between_18_and_64,between_65_and_66,between_67_and_69,between_70_and_74,between_75_and_79,
	between_80_and_84,between_85_and_up
)
	SELECT
	SUBSTRING(F.GEOID,10,21),
	F.ACS5_END_YEAR,
	U.B01002003_EST,
	F.B01001026_EST,
	F.B01001027_EST,
	F.B01001028_EST,
	F.B01001029_EST,
	F.B01001030_EST,
	(	(F.B01001026_EST)-
		(F.B01001027_EST+F.B01001028_EST+F.B01001029_EST+
		 F.B01001030_EST+F.B01001044_EST+F.B01001045_EST+
		 F.B01001046_EST+F.B01001047_EST+F.B01001048_EST+
	     F.B01001049_EST)
	),
	F.B01001044_EST,
	F.B01001045_EST,
	F.B01001046_EST,
	F.B01001047_EST,
	F.B01001048_EST,
	F.B01001049_EST
	FROM _G_B01001 AS F JOIN _G_B01002 AS U
		ON (F.GEOID = U.GEOID AND F.ACS5_END_YEAR = U.ACS5_END_YEAR)
GO