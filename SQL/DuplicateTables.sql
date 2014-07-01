USE tHUB
GO
DROP TABLE B_Age
GO

USE tHUB
GO
CREATE TABLE B_Age
(
	geoid char(21) primary key,
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
	between_85_and_up int
)
GO

GO
INSERT INTO B_Age 
(
	geoid,total,between_0_and_5,between_5_and_9,between_10_and_14,between_15_and_17,
	between_18_and_64,between_65_and_66,between_67_and_69,between_70_and_74,between_75_and_79,
	between_80_and_84,between_85_and_up
)
	SELECT
	M.GEOID,
	M.B01001002_EST+F.B01001026_EST,
	M.B01001003_EST+F.B01001027_EST,
	M.B01001004_EST+F.B01001028_EST,
	M.B01001005_EST+F.B01001029_EST,
	M.B01001006_EST+F.B01001030_EST,
	(	M.B01001002_EST-M.B01001002_EST+F.B01001026_EST+M.B01001003_EST+F.B01001027_EST+
	                    M.B01001004_EST+F.B01001028_EST+M.B01001005_EST+F.B01001029_EST+
		                M.B01001006_EST+F.B01001030_EST
	),
	M.B01001020_EST+F.B01001044_EST,
	M.B01001021_EST+F.B01001045_EST,
	M.B01001022_EST+F.B01001046_EST,
	M.B01001023_EST+F.B01001047_EST,
	M.B01001024_EST+F.B01001048_EST,
	M.B01001025_EST+F.B01001049_EST
	FROM B_B01001 AS M JOIN B_B01001 AS F
		ON (M.GEOID = F.GEOID)
GO