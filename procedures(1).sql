delimiter //
create definer=`root`@`localhost` procedure `drops`(in c char(20), in id char(10), out a integer)
begin
	declare temp char(20);
	declare transactionerror int default 0;
	declare continue handler for sqlexception set transactionerror = 1;

	start transaction;

	set temp = (select UoSCode from transcript where StudId = id and Grade is NULL and UoSCode = c);
	if temp is NULL then
		set a = 1;
	else
		update uosoffering set Enrollment = Enrollment - 1
		where UoSCode = c and Semester = (select semester from transcript where UoSCode = c and StudId = id)
		and year = (select year from transcript where UoSCode = c and StudId = id);	
		delete from transcript where StudId = id and UoSCode = C;
		SET a = 0;
	end if;

	if (transactionerror = 1) then 
	begin 
		set a = 2;
		rollback;
	end;
	else 
	begin
		commit;
	end;
	end if;
end//

create definer=`root`@`localhost` procedure `updatepersonalinformation`(in new_content char(20), in change_option char(20), in stdname char(30), out a integer)
begin
	declare temp char(20);
	declare transactionerror int default 0;
	declare continue handler for sqlexception set transactionerror = 1;

	start transaction;
    
    if change_option = "password" then
		set a=0;
		update student set Password=new_content where Name=stdname;
	elseif change_option = "address" then
		set a=0;
		update student set Address=new_content where Name=stdname;
	else
		set a=1;
    end if;
    

	if (transactionerror = 1) then 
	begin 
		set a = 2;
		rollback;
	end;
	else 
	begin
		commit;
	end;
	end if;
end//


create definer=`root`@`localhost` procedure `enroll`(in c char(20), in s char(10), in y char(10), in id char(10), out result integer, out req char(20))
begin 
	declare a integer;
	declare b integer;
	declare d char(20);
	declare e integer;
	declare f integer;
	declare transactionerror int default 0;
	declare continue handler for sqlexception set transactionerror = 1;

	start transaction;

	set req = null;
	set a = (select count(*) from requires where UoSCode = c);
	set b = (select count(*) from uosoffering where UoSCode = c and Semester = s and Year = y and Enrollment < MaxEnrollment);
	set e = (select count(*) from transcript where UoSCode = c and StudId = id);
	if e = 0 then 
		if a = 0 and b = 1 then 
			insert into transcript values(id, c, s, y, NULL);
			update uosoffering set Enrollment = Enrollment + 1 where UoSCode = c and Semester = s and Year = y;
			set result = 1;
		elseif a = 1 and b = 1 then
			set d = (select grade from transcript where UoSCode = (select PrereqUoSCode from requires where UoSCode = c) and StudId = id);
			if d = 'CR' or d = 'P' then 
				insert into transcript values(id, c, s, y, NULL);
				update uosoffering set Enrollment = Enrollment + 1 where UoSCode = c and Semester = s and Year = y;
				set result = 1;
			else 
				set result = 2;
			end if;
		elseif a > 1 and b = 1 then
			set f = (select count(*) from requires s left outer join transcript t on (s.PrereqUoSCode = t.UoSCode) where s.UoSCode = c and StudId = id and (grade = 'CR' or grade = 'P'));
			if a = f then
				insert into transcript values(id, c, s, y, NULL);
				update uosoffering set Enrollment = Enrollment + 1 where UoSCode = c and Semester = s and Year = y;
				set result = 1;
			else
				set result = 5;
			end if;
		elseif a > 1 and b = 0 then 
			set f = (select count(*) from requires s left outer join transcript t on (s.PrereqUoSCode = t.UoSCode) where s.UoSCode = c and StudId = id and (grade = 'CR' or grade = 'P'));
			if a = f then 
				insert into transcript values(id, c, s, y, NULL);
				update uosoffering set Enrollment = Enrollment + 1 where UoSCode = c and Semester = s and Year = y;
				set result = 4;
			else 
				set result = 6;
			end if;
		elseif a = 1 and b = 0 then
			set d = (select grade from transcript where UoSCode = (select PrereqUoSCode from requires where UoSCode = c) and StudId = id);
			if d = 'CR' or d = 'P' then 
				set result = 4;
			else
				set result = 3;
			end if;
		elseif a = 0 and b = 0 then 
			set result = 4;
		end if;
	else
		set result = 0;
	end if;

	if (transactionerror = 1) then 
	begin 
		set result = 10;
		rollback;
	end;
	else 
	begin
		commit;
	end;
	end if;
end //


delimiter //
create trigger check_enroll_percent before update on uosoffering
for each row
begin 
	update enrollpercent set percent = new.enrollment / new.maxenrollment where id = '1';
end;
