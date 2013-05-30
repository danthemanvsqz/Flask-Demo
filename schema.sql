drop table if exists contacts;
create table contacts(
	id integer primary key autoincrement,
	lname string not null,
	fname string not null,
	email string,
	phone string
);