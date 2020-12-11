create or replace trigger update_book_cnt
after insert
on ORDER_DETAILS
for each row
DECLARE
	ID INTEGER;
	Q INTEGER;
BEGIN
	ID := :NEW.BOOK_ID;
	Q := :NEW.QUANTITY;
	UPDATE BOOK SET TOTAL_SOLD = TOTAL_SOLD +Q WHERE BOOK_ID = ID;
END;
/