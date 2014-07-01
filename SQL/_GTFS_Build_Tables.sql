USE tHUB 

IF OBJECT_ID ('GTFS_Agency', 'U') is not null
DROP TABLE GTFS_Agency
GO
CREATE TABLE GTFS_Agency 
(
  /* primary key should be agency_id, but have to be assigned*/
  agency_id int,
  agency_name text not null,
  agency_url text not null,
  agency_timezone text,
  agency_lang text,
  agency_phone text,
  agency_fare_url text
)
GO

IF OBJECT_ID ('GTFS_Calendar', 'U') is not null
DROP TABLE GTFS_Calendar
GO
CREATE TABLE GTFS_Calendar 
(
  service_id int primary key,
  monday int not null,
  tuesday int not null,
  wednesday int not null,
  thursday int not null,
  friday int not null,
  saturday int not null,
  sunday int not null,
  start_date date not null, 
  end_date date not null
)
GO

IF OBJECT_ID ('GTFS_Calendar_Dates', 'U') is not null
DROP TABLE GTFS_Calendar_Dates
GO
CREATE TABLE GTFS_Calendar_Dates
(
  service_id int primary key,
  calendar_date  date not null,
  exception_type int
)
GO

IF OBJECT_ID ('GTFS_Routes', 'U') is not null
DROP TABLE GTFS_Routes
GO
CREATE TABLE GTFS_Routes 
(
  route_id	int primary key,
  agency_id   int not null,
  route_short_name text default '',
  route_long_name text default '',
  route_desc text,
  route_type int,
  route_url  text,
  route_color char(6),
  route_text_color char(6)
)
GO

IF OBJECT_ID ('GTFS_Route_Types', 'U') is not null
DROP TABLE GTFS_Route_Types
GO
CREATE TABLE GTFS_Route_Types
(
  route_type int primary key,
  descript text
)
INSERT INTO GTFS_Route_Types (route_type, descript) VALUES (0, 'Street Level Rail');
INSERT INTO GTFS_Route_Types (route_type, descript) VALUES (1, 'Underground Rail');
INSERT INTO GTFS_Route_Types (route_type, descript) VALUES (2, 'Intercity Rail');
INSERT INTO GTFS_Route_Types (route_type, descript) VALUES (3, 'Bus');
INSERT INTO GTFS_Route_Types (route_type, descript) VALUES (4, 'Ferry');
INSERT INTO GTFS_Route_Types (route_type, descript) VALUES (5, 'Cable Car');
INSERT INTO GTFS_Route_Types (route_type, descript) VALUES (6, 'Suspended Car');
INSERT INTO GTFS_Route_Types (route_type, descript) VALUES (7, 'Steep Incline Mode');
GO

IF OBJECT_ID ('GTFS_Trips', 'U') is not null
DROP TABLE GTFS_Trips
GO
CREATE TABLE GTFS_Trips
(
  route_id int not null, 
  service_id int not null,
  trip_id int primary key,
  trip_headsign text,
  direction_id  int not null,
  block_id int not null,
  shape_id int not null,  
)
GO

IF OBJECT_ID ('GTFS_Stops', 'U') is not null
DROP TABLE GTFS_Stops
GO
CREATE TABLE GTFS_Stops
(
  stop_id    int primary key,
  stop_code  text,
  stop_name  text not null, 
  stop_lat   float not null,
  stop_lon   float not null,
  zone_id    text,
  stop_url   text,
  location_type text,
  parent_station text
)
GO

IF OBJECT_ID ('GTFS_Stop_Times', 'U') is not null
DROP TABLE GTFS_Stop_Times
GO
CREATE TABLE GTFS_Stop_Times 
(
  /* primary key = trip_id+arrival_time+stop_id */
  trip_id int not null, 
  arrival_time time not null,
  departure_time time not null,
  stop_id int not null, 
  stop_sequence int not null,
  stop_headsign text,
  pickup_type   int ,
  drop_off_type int , 
  shape_dist_traveled float,
  arrival_day int not null,
  departure_day int not null
)
GO

IF OBJECT_ID ('GTFS_Shapes', 'U') is not null
DROP TABLE GTFS_Shapes
GO
CREATE TABLE GTFS_Shapes (
  shape_id int not null, 
  shape_pt_lat float not null, 
  shape_pt_lon float not null,
  shape_pt_sequence int not null,
  shape_dist_traveled float not null
)
GO

IF OBJECT_ID ('GTFS_Frequencies', 'U') is not null
DROP TABLE GTFS_Frequencies
GO
CREATE TABLE GTFS_Frequencies (
  /* primary key = trip_id+start_time+end_time */
  trip_id     int not null,
  start_time  time not null,
  end_time    time not null,
  headway_secs int not null,
  exact_times int,
  start_time_seconds int,
  end_time_seconds int
)
GO

IF OBJECT_ID ('GTFS_Transfers', 'U') is not null
DROP TABLE GTFS_Transfers
GO
CREATE TABLE GTFS_Transfers (
  /* primary key = from_stop_id+to_stop_id */
  from_stop_id int not null,
  to_stop_id int not null,
  transfer_type int,
  min_transfer_time int,
)
GO

IF OBJECT_ID ('GTFS_Transfer_Types', 'U') is not null
DROP TABLE GTFS_Transfer_Types
GO
CREATE TABLE GTFS_Transfer_Types (
  transfer_type int primary key,
  descript text
)
INSERT INTO GTFS_Transfer_Types (transfer_type, descript) VALUES (0,'Preferred transfer point');
INSERT INTO GTFS_Transfer_Types (transfer_type, descript) VALUES (1,'Designated transfer point');
INSERT INTO GTFS_Transfer_Types (transfer_type, descript) VALUES (2,'Transfer possible with min_transfer_time window');
INSERT INTO GTFS_Transfer_Types (transfer_type, descript) VALUES (3,'Transfers forbidden');
GO

IF OBJECT_ID ('GTFS_Feed_Info', 'U') is not null
DROP TABLE GTFS_Feed_Info
GO
CREATE TABLE GTFS_Feed_Info (
  feed_publisher_name text not null,
  feed_publisher_url text not null,
  feed_timezone text,
  feed_lang text,
  feed_version text,
  feed_start_date text not null,
  feed_end_date text not null
)
GO

