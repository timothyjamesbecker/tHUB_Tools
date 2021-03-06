USE tHUB
BEGIN TRAN /* default read committed isolation level is fine */
DECLARE @ID int = 2
IF NOT EXISTS (SELECT @ID FROM GTFS_Agency WITH (UPDLOCK, ROWLOCK, HOLDLOCK) WHERE agency_id=@ID)
    INSERT INTO GTFS_Agency VALUES (2,'Test Agency','http://testagency.gov',null,null,null,null) /* insert */
ELSE /* update */
COMMIT /* locks are released here */

USE tHUB
BEGIN TRAN
INSERT INTO GTFS_Agency
VALUES (4,'Test Agency','http://testagency.gov',null,null,null,null)
COMMIT

SELECT * FROM GTFS_Agency