CREATE OR REPLACE PROCEDURE RESTORE_BOOK (ID IN INTEGER) IS
	cnt1 INTEGER;
	cnt2 INTEGER;
	cnt3 INTEGER;
	tbook_id INTEGER;
	tbook_name VARCHAR2(512);
	tbook_genre VARCHAR2(512);
	tbook_edition VARCHAR2(512);
	tauthor_id INTEGER;
	tpublisher_id INTEGER;
	tauthor_name VARCHAR2(512);
	tpublisher_name VARCHAR2(512);
	tprice INTEGER;
	tdiscount INTEGER;
	tcountry VARCHAR2(128);
	tlanguage VARCHAR2(128);
	tsummary VARCHAR2(3000);
	tISBN VARCHAR2(100);
	tpages INTEGER;
	ttotal_sold INTEGER;
	tratings decimal(3,2);
	tno_of_ratings INTEGER;
BEGIN
	SELECT BOOK_ID , BOOK_NAME, BOOK_GENRE , BOOK_EDITION , AUTHOR_NAME , PUBLISHER_NAME , PRICE , DISCOUNT , COUNTRY , LANGUAGE,SUMMARY , ISBN , PAGES,TOTAL_SOLD , RATINGS , NO_OF_RATINGS INTO tbook_id,tbook_name,tbook_genre,tbook_edition,tauthor_name,tpublisher_name,tprice,tdiscount,tcountry,tlanguage,tsummary,tISBN,tpages,ttotal_sold,tratings,tno_of_ratings FROM DELETED_BOOK WHERE BOOK_ID= ID;
	
	
	SELECT COUNT(*) INTO cnt1 FROM BOOK WHERE BOOK_ID = ID;
	SELECT COUNT(*) INTO cnt2 FROM AUTHOR WHERE AUTHOR_NAME = tauthor_name;
	SELECT COUNT(*) INTO cnt3 FROM PUBLISHER WHERE PUBLISHER_NAME = tpublisher_name;
	
	IF cnt1 = 1 THEN
		SELECT MAX(BOOK_ID)+1 INTO tbook_id FROM BOOK;
	END IF;
	
	IF cnt2 = 1 THEN
		SELECT AUTHOR_ID INTO tauthor_id FROM AUTHOR WHERE AUTHOR_NAME = tauthor_name;
	ELSE
		SELECT MAX(AUTHOR_ID)+1 INTO tauthor_id FROM AUTHOR;
		INSERT INTO AUTHOR (AUTHOR_ID,AUTHOR_NAME) VALUES (tauthor_id ,tauthor_name );
	END IF;
	
	IF cnt3 = 1 THEN
		SELECT PUBLISHER_ID INTO tpublisher_id FROM PUBLISHER WHERE PUBLISHER_NAME = tpublisher_name;
	ELSE
		SELECT MAX(PUBLISHER_ID)+1 INTO tpublisher_id FROM PUBLISHER;
		INSERT INTO PUBLISHER (PUBLISHER_ID,PUBLISHER_NAME) VALUES (tpublisher_id ,tpublisher_name );
	END IF;
	
	insert into BOOK values(tbook_id,tbook_name,tbook_genre,tbook_edition,tauthor_id,tpublisher_id,tprice,tdiscount,tcountry,tlanguage,tsummary,tISBN,tpages,ttotal_sold,tratings,tno_of_ratings);
	
	DELETE FROM DELETED_BOOK WHERE BOOK_ID = ID;
	
	
EXCEPTION
	WHEN NO_DATA_FOUND THEN
		DBMS_OUTPUT.PUT_LINE('No data found.') ;
	WHEN TOO_MANY_ROWS THEN
		DBMS_OUTPUT.PUT_LINE('More than one data found.') ;
	WHEN OTHERS THEN
		DBMS_OUTPUT.PUT_LINE('Some unknown error occurred.') ;
END;
/