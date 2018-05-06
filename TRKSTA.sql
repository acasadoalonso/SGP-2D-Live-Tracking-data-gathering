use APRSLOG;
DROP   VIEW TRKSTA;
CREATE VIEW TRKSTA as select *, (select registration from GLIDERS where GLIDERS.idglider = SUBSTRING(OGNTRKSTATUS.id,4,6)) as TRK_NAME from OGNTRKSTATUS;
