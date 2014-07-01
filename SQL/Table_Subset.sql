USE tHUB
GO
SELECT * FROM _B_B01001 WHERE ACS5_END_YEAR = 2010 /* superset data has all of 2010+2011 */
EXCEPT
SELECT * FROM _B_B01001_2010 /* subset data only has half of super 2010 */
GO