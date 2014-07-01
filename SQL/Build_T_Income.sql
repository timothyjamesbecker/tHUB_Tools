USE tHUB
GO

/* clear constraints which cleans out the multi-primary key*/
DECLARE @database nvarchar(50)
DECLARE @table nvarchar(50)
SET @database = 'tHUB'
SET @table = 'ACS_T_Income'
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
IF OBJECT_ID ('ACS_T_Income', 'U') IS NOT NULL 
DROP TABLE ACS_T_Income
GO

CREATE TABLE ACS_T_Income
(
	geoid char(11) not null,
	acsyear int not null,
	median int,
	below_100 int,
	above_100_below_150 int,
	above_150 int,
	between_loss_and_10k int,
	between_10k_and_15k int,
	between_15k_and_25k int,
	between_25k_and_35k int,
	between_35k_and_50k int,
	between_50k_and_65k int,
	between_65k_and_75k int,
	between_75k_and_up int,
	CONSTRAINT ACS_T_Income_pk primary key (geoid,acsyear)
)
GO

INSERT INTO ACS_T_Income
(
		geoid, acsyear,median, below_100, above_100_below_150, above_150, 
		between_loss_and_10k, between_10k_and_15k, between_15k_and_25k, between_25k_and_35k, 
		between_35k_and_50k, between_50k_and_65k, between_65k_and_75k, between_75k_and_up
)
	SELECT
	SUBSTRING(I.GEOID,10,20), I.ACS5_END_YEAR,M.B06011001_EST, P.B06012001_EST, P.B06012003_EST, P.B06012004_EST,
	(I.B06010002_EST+I.B06010004_EST), --between_los_and_10
	I.B06010005_EST,                   --between_10_and_15
	I.B06010006_EST,                   --between_15_and_25
	I.B06010007_EST,                   --between_25_and_35
	I.B06010008_EST,                   --between_35_and_50
	I.B06010009_EST,                   --between_50_and_65
	I.B06010010_EST,                   --between_65_and_75
	I.B06010011_EST                    --between_75_and_up
	 
	FROM _T_B06010 AS I 
		JOIN _T_B06011 AS M
			ON (I.GEOID = M.GEOID AND I.ACS5_END_YEAR = M.ACS5_END_YEAR)
		JOIN _T_B06012 AS P
			ON (M.GEOID = P.GEOID AND M.ACS5_END_YEAR = P.ACS5_END_YEAR)
GO