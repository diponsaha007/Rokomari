create or replace trigger backup_deleted_books
before delete
on book
for each row
declare
		t_book_id INTEGER ;
		t_book_name VARCHAR2(512);
		t_book_genre VARCHAR2(512);
		t_book_edition VARCHAR2(512);
		t_author_id INTEGER;
		t_publisher_id INTEGER ;
		t_price INTEGER ;
		t_discount INTEGER;
		t_country VARCHAR2(128);
		t_language VARCHAR2(128);
		t_summary VARCHAR2(3000);
		t_ISBN VARCHAR2(100);
		t_pages INTEGER;
		t_total_sold INTEGER;
		t_ratings decimal(3,2);
		t_no_of_ratings INTEGER;
		t_datetime date;
begin
		t_book_id := :old.book_id;
		t_book_name := :old.book_name;
		t_book_genre := :old.book_genre;
		t_book_edition := :old.book_edition;
		t_author_id := :old.author_id;
		t_publisher_id  := :old.publisher_id;
		t_price  := :old.price;
		t_discount := :old.discount;
		t_country := :old.country;
		t_language := :old.language;
		t_summary := :old.summary;
		t_ISBN := :old.ISBN;
		t_pages := :old.pages;
		t_total_sold := :old.total_sold;
		t_ratings := :old.ratings;
		t_no_of_ratings := :old.no_of_ratings;
		t_datetime := SYSDATE;
	  insert into deleted_book values(t_book_id, t_book_name, t_book_genre, t_book_edition, t_author_id, t_publisher_id,
		t_price, t_discount, t_country, t_language, t_summary, t_ISBN, t_pages, t_total_sold, t_ratings, t_no_of_ratings,
		t_datetime);
EXCEPTION
	WHEN OTHERS THEN
		DBMS_OUTPUT.PUT_LINE('Some unknown error occurred.') ;
end;
/
