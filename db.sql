
drop database if exists csdn_semantics_db;

create database if not exists csdn_semantics_db default character set utf8 collate utf8_general_ci;
use csdn_semantics_db;
create table if not exists csdn_semantics_info(linkmd5id char(32) NOT NULL, title text, link text, description text, updated datetime DEFAULT NULL, primary key(linkmd5id)) ENGINE=MyISAM DEFAULT CHARSET=utf8;
select * from csdn_semantics_info;

