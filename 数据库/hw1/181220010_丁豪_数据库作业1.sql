create database homework1;
use homework1;
create table Customers(
	cid char(4) not null,
    cname char(20) not null,
    city char(20),
    discnt real,
    primary key(cid));
create table Agents(
	aid char(3) not null,
    aname char(20) not null,
    city char(20),
    perc smallint,
    primary key(aid));
create table Products(
	pid char(3) not null,
    pname char(20) not null,
    city char(20),
    quantity int not null,
    price real not null,
    primary key(pid));
create table Orders(
	ordno int not null,
    orddate date not null,
    cid char(4) not null,
    aid char(3) not null,
    pid char(3) not null,
    qty int,
    dols real,
    primary key(ordno));
    
    
    
    
    
    
    insert into customers(cid,cname,city,discnt)
values
('c001', 'Tiptop', 'Duluth', 10.00),
('c002', 'Basics', 'Dallas', 12.00),
('c003', 'Allied', 'Dallas', 8.00),
('c004', 'ACME', 'Duluth', 8.00),
('c006', 'ACME', 'Kyoto', 0.00);

insert into agents(aid,aname,city,perc)
values
('a01', 'Smith', 'New York', 6),
('a02', 'Jones', 'Newark',   6),
('a03', 'Brown', 'Tokyo',    7),
('a04', 'Gray',  'New York', 6),
('a05', 'Otasi', 'Duluth',   5),
('a06', 'Smith', 'Dallas',   5);

insert into products(pid,pname,city,quantity,price)
values
('p01', 'comb',   'Dallas', 111400, 0.50),
('p02', 'brush',  'Newark', 203000, 0.50),
('p03', 'razor',  'Duluth', 150600, 1.00),
('p04', 'pen',    'Duluth', 125300, 1.00),
('p05', 'pencil',  'Dallas', 221400, 1.00),
('p06', 'folder',  'Dallas', 123100, 2.00),
('p07', 'case',   'Newark', 100500, 1.00);

insert into orders(ordno,orddate,cid,aid,pid,qty,dols)
values
(1011, '2016-01-08', 'c001', 'a01', 'p01', 1000, 450.00),
(1012, '2016-01-12', 'c001', 'a01', 'p01', 1000, 450.00),
(1019, '2016-02-24', 'c001', 'a02', 'p02', 400,  180.00),
(1017, '2016-02-10', 'c001', 'a06', 'p03', 600,  540.00),
(1018, '2016-02-16', 'c001', 'a03', 'p04', 600,  540.00),
(1023, '2016-03-12', 'c001', 'a04', 'p05', 500,  450.00),
(1022, '2016-03-08', 'c001', 'a05', 'p06', 400,  720.00),
(1025, '2016-04-07', 'c001', 'a05', 'p07', 800,  720.00),
(1013, '2016-01-13', 'c002', 'a03', 'p03', 1000, 880.00),
(1026, '2016-05-20', 'c002', 'a05', 'p03', 800,  704.00),
(1015, '2016-01-23', 'c003', 'a03', 'p05', 1200, 1104.00),
(1014, '2016-01-18', 'c003', 'a03', 'p05', 1200, 1104.00),
(1021, '2016-02-28', 'c004', 'a06', 'p01', 1000, 460.00),
(1016, '2016-01-25', 'c006', 'a01', 'p01', 1000, 500.00),
(1020, '2016-02-05', 'c006', 'a03', 'p07', 600,  600.00),
(1024, '2016-03-12', 'c006', 'a06', 'p01', 800,  400.00);







use homework1;
select distinct aid 
from agents 
where aid not in (
select aid 
from orders 
where cid in (
select cid 
from customers 
where city='Duluth'));

select distinct aid 
from orders 
where cid in (select distinct cid from customers where city='Duluth' or city='Kyoto')
group by aid,pid 
having count(distinct cid)=(select count(cid) from (select cid from customers where city='Duluth' or city='Kyoto')as p); 

select distinct cid 
from customers 
where cid not in(
select distinct cid 
from orders 
where aid<>'a03' and aid<>'a05');


select pid from(
	select pid,city from 
	(select pid,cid from orders) as o 
	inner join 
	(select cid,city from customers) as c 
	on o.cid=c.cid) as product_city
group by pid 
having count(distinct product_city.city)=(select distinct count(city) from customers);

select cid,orddate from orders as t
where(
	select count(*) 
	from orders as tt
	where tt.cid=t.cid and tt.ordno>t.ordno
)<2 
order by cid,orddate ;

select pid from orders as o1  
where o1.cid in (select cid from customers where city='Dallas') 
group by pid 
having count(distinct cid)=(select count(cid) from customers where city='Dallas');

select aid,perc from agents 
where aid in(
	select distinct aid from orders as o1
    where o1.cid in (select distinct cid from customers where city='Duluth') 
    group by aid 
    having count(distinct cid)=(select distinct count(cid) from customers where city='Duluth')
)
order by perc desc;

select distinct pid from orders as o1 
where 
(select city from customers as c1 where o1.cid=c1.cid)
=(select city from agents as a1 where a1.aid=o1.aid);

select distinct aid from agents as a1
where a1.perc=(select max(perc) from agents);
select distinct aid from agents as a1 
where a1.perc>=all(select perc from agents as a2);

select cid,sum(dols) from orders where cid in(
select cid from orders as o1
where o1.aid='a04' 
and o1.cid not in (select cid from orders as o2 where o2.aid<>'a04'))
group by cid;

select * from(select pid,aid,sum(qty) as ss from orders group by pid,aid) as t 
where t.ss>1000 and 
	(select count(pid) 
	from (select pid,aid,sum(qty) as ss from orders group by pid,aid) as tt 
    where tt.pid=t.pid and tt.ss>t.ss
    )<3
order by pid,aid;

select distinct cid from customers where cid not in(
	select distinct cid from(
		select cid,pid,avg(qty) as av from orders
		group by cid,pid
		order by cid,pid) as t
	where t.av<300);






drop table orders;
drop table customers;
drop table agents;
drop table products;
drop database homework1;