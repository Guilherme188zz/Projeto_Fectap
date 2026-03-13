/*
 * sql/db.psql: script to build the gnuvet database in postgres
 *   TAKE CARE THIS IS FOR DEVEL.  PRODUCTION NEEDS DIFFERENT.
 * Copyright (c) 2015 Dipl.Tzt. Enno Deimel <ennodotvetatgmxdotnet>
 *
 * This file is part of gnuvet, published under the GNU General Public License
 * version 3 or later (GPLv3+ in short).  See the file LICENSE for information.
 *
 * After having created the gnuvet db, aptly named `gnuvet'
 * -- for instance with /usr/bin/createdb -- on the db machine, you can roll
 * in this script like so: $ psql gnuvet < db.psql
 * This should be performed as user 'gnuvet'.
 */

-- TODO:
--  solve vacc reminders

\c postgres
drop database if exists gnuvet;
--drop role if exists gvuser;
--drop role if exists gnuvet; -- this won't work being logged in as gnuvet! Put in shell script.  Think of psql serving not only gnuvet...
-- create role gnuvet createdb createrole login encrypted password 'GnuVetPassword' replication;
-- create role gvuser login; -- this for later, the -- well -- gvusers group
-- grant connect temp

-- test 150223:
set client_encoding to 'UTF-8';
create database gnuvet encoding 'UTF-8'; -- test 150223

\c gnuvet
create table century(cent serial primary key); -- will psql & gv exist in 2100?

create table boxroles(
 boxr_id serial primary key,
 boxr_name varchar(120) not null);
-- 'master server', 'local server', 'workstation' etc.

create table staffroles(
 staffrole_id serial primary key,
 staffrole_name varchar(20) not null);

create table titles(
 t_id serial primary key,
 t_title varchar(20) not null);

create type sex as enum('m', 'f', 'h', 'n', 'n/a');

create table markups(
 m_id serial primary key,
 m_name varchar(30) not null,
 m_rate numeric(4,3) not null,
 m_obs boolean not null default FALSE);

-- product type: med other serv cons hist good food
create table ptypes(
 pt_id serial primary key,
 pt_name varchar(10) not null,
 pt_col varchar(20) not null,
 pt_markup int not null default 1 references markups);

-- create type ptype as enum('con','hst','med','vac','srv','god','fod','oth');

create table addresses(
 addr_id serial primary key,
 housen varchar(80) not null default '',
 street varchar(80) not null default '',
 village varchar(80) not null default '',
 city varchar(80) not null default '',
 region varchar(80) not null default '',
 postcode varchar(10) not null default '');

create table branches(
 branch_id serial primary key,
 branch_name varchar(120) not null,
 branch_address int not null default 1 references addresses,
 branch_tel varchar(30),
 branch_mobile varchar(30),
 branch_fax varchar(30),
 branch_email varchar(120),
 branch_vatreg varchar(20),
 branch_currency varchar(5),
 branch_currencysymbol varchar(3));

create table boxes( -- computers in gnuvet network
 box_id serial primary key,
 box_name varchar(80) not null, --  'Surgery1', 'Reception2' etc.
 box_ipv4 inet unique not null,
 box_branch int not null default 1 references branches,
 box_role int references boxroles not null);

create table staff(
 stf_id serial primary key,
 stf_func int not null default 2 references staffroles,
 stf_title int not null default 3 references titles,
 stf_sex sex not null default 'n',
 stf_surname varchar(80) not null,
 stf_mname varchar(25) not null default '',
 stf_forename varchar(80) not null,
 stf_short varchar(10) unique not null,
 stf_logname varchar(10) unique not null,
 stf_tel varchar(30),
 stf_mobile varchar(30),
 stf_email varchar(120));

create table clients(
 c_id serial primary key,
 c_title int not null default 3 references titles,
 c_sname varchar(80) not null,
 c_mname varchar(25) not null default '',
 c_fname varchar(80) not null default '',
 c_address int not null default 1 references addresses,
-- c_telhome varchar(30) not null default '',
-- c_telwork varchar(30) not null default '',
-- c_mobile1 varchar(30) not null default '',
-- c_mobile2 varchar(30) not null default '',
 c_email varchar(120) not null default '',
 baddebt boolean not null default False,
 c_reg date not null default current_date,
 c_last timestamp not null default current_timestamp,
 c_anno varchar(255) not null default '');

create table phones( -- client phones
-- phone_id serial primary key,
 phone_cid int not null references clients,
 phone_opt smallint not null default 1, -- 1 best
 phone_num varchar(25) not null default '',
 phone_anno varchar(25) not null default '',
 unique(phone_cid,phone_num));

-- keys presumably overkill for up to medium-sized practice:
--create index c_sname on clients(c_sname);
--create index c_fname on clients(c_fname);
--create index c_last on clients(c_last)

create table locations(
 l_id serial primary key,
 l_name varchar(80) not null,
 l_address int not null default 1 references addresses,
 l_tel varchar(30) default '',
 l_mobile varchar(30) default '',
 l_anno varchar(255) not null default '');

-- keys presumably overkill for up to medium-sized practice

create table species(
 spec_id serial primary key,
 spec_name varchar(80) unique not null,
-- spec_code char(1) unique not null,
-- this to replaced by function 1<<id-1
 spec_fa boolean not null default TRUE); -- potential food animal
-- actually mostly genus/order not species

create table breeds(
 breed_id serial primary key,
 b_spec int references species not null,
 breed_name varchar(80) unique not null,
 breed_abbr varchar(5) unique not null);

create table basecolours(
 bcol_id serial primary key,
 bcol varchar(25) unique,
-- bc_combine colcombine not null default 'y',
-- this to be bit(1) for null (none), 0 (poss), 1 (must)
 bc_combine bit(1) default '0',
 bc_spec int not null);

create table colours(
 col_id serial primary key,
-- c_speccode varchar(120) not null,
-- c_speccode int not null, -- redundant: or bc_spec
 col1 int references basecolours not null,
 col2 int references basecolours not null,
 col3 int references basecolours not null,
 unique (col1,col2,col3));

create table insurances(
 i_id serial primary key,
 i_name varchar(80) not null,
 i_email varchar(120),
 i_rep varchar(120),
 i_address int not null default 1 references addresses,
 i_tel varchar(30),
 i_anno varchar(255) not null default '');

create table chronics(
 chr_id serial primary key,
 chr_name varchar(80) not null);

create table patients(
 p_id serial primary key,
 p_name varchar(80) not null,
 p_cid int references clients not null,
 breed int references breeds,
 xbreed boolean not null default False,
 dob date,
 dobest boolean not null default False,
 colour int references colours,
 sex sex,
 neutd boolean default False,
 vicious boolean not null default False,
 p_reg date default current_date,
 p_anno varchar(255) not null default '',
 loc int references locations,
 identno varchar(20),
 petpass varchar(20),
 rip boolean not null default False,
 p_last timestamp,
 ins int references insurances,
 chr int not null default 0); --> chronic problems, 1<<chr-1 bitmask

create index p_name_idx on patients(p_name);

-- maybe redundance, but i think eases search for patient seen some date:
create table seen(
 seen_pid int not null references patients, 
 seen_date date not null);

create index seen_pid_idx on seen(seen_pid);

create table neuts(
 neut_id int not null references patients,
 neut_date date);

create table rips(
 rip_id int not null references patients,
 rip_date timestamp not null);

create table ownerhist(
 oh_id serial primary key,
 oh_pid int not null references patients,
 oh_prev int not null references clients,
 oh_date date not null);

create table namehist(
 nh_id serial primary key,
 nh_pid int not null references patients,
 nh_name varchar(80) not null default '',
 nh_date date not null);

create table vats(
 vat_id serial primary key,
 vat_name varchar(30) not null,
 vat_rate numeric(5,4) not null,
 vat_obs boolean not null default FALSE);

create table units(
 u_id serial primary key,
 u_name varchar(20) not null,
 u_pl varchar(20) not null,
 u_abbr varchar(5) not null,
 u_short varchar(1) unique not null default '');

create table categories(
 cat_id serial primary key,
 category varchar(40) not null unique);

create table ingredients(
 ingr_id serial primary key,
 ingredient varchar(50) not null unique,
 ingr_catid int references categories); -- not null?

create table suppliers(
 s_id serial primary key,
 s_name varchar(80) not null,
 s_rep varchar(120),
 s_email varchar(80),
 s_address int not null default 1 references addresses,
 s_tel varchar(30),
 s_fax varchar(30),
 s_mobile varchar(30));

/*  collection of building blocks for medication instructions */
create table instructions(
 inst_id serial primary key,
 inst_abbr varchar(5) not null,
 inst_txt varchar(90) not null,
 inst_pos int not null,
 unique (inst_abbr, inst_pos));

/* collection of printed label texts for re-use */
create table labels(
 lb_id serial primary key,
 lb_abbr varchar(15) unique,
 lb_txt varchar(255) unique);

create table paymodes(pm_id serial primary key,pm_mode varchar(20) not null,pm_ck bool not null default TRUE);

create table products(
 pr_id serial primary key,
 pr_name varchar(80) not null,
 pr_short varchar(10) not null,
 pr_type int not null default 1 references ptypes,
 pr_pprice numeric(8,2) not null default 0.00, -- net purchase price
 pr_nprice numeric(8,2) not null, -- net sale price
 pr_since date not null default '2010-01-01',
 pr_vat int default 1 references vats,
 pr_perm boolean not null default FALSE, -- 0 OTC,  1 POM
 pr_u int not null references units,
 pr_limit int not null default 0,
-- pr_ingr int references ingredients, -- bitmask? separate table! if at all
 pr_instr boolean not null default TRUE -- ask for instructions
-- pr_upordu numeric(8,4), -- for assistance in price calc -- whatsthis?
);

create table stocks(
 st_id serial primary key,
 st_prid int not null references products,
 st_batch varchar(30) not null,
 st_num numeric(9,2) not null);

/* create table barcodes(
 bcode_id serial primary key,
 bcode_prid int references products;
 bcode_val int);

create table batchnos( -- how should that work?
 chb_id serial primary key,
 chb_prid int not null references products,
 chb_val varchar(30) not null);

create table pr_supplier(
 prid int not null references products,
 prsup int references suppliers,
 prordid varchar(100));
****************/

create table pricehist( -- more efficient than obsoleting old prodprices
 pop_id serial primary key,
 pop_prid int not null references products,
 pop_npr numeric(8,2) not null,
 pop_vat int not null references vats,
 pop_todate date not null,
 pop_reason varchar(100) not null default '');

/*
create table toorder(o_prid int not null references products, o_date date);
**************/

/* 'validity' for vaccinations */
create table validities(
 val_id serial primary key,
 val_text varchar(255) not null,
 val_days int not null);

create table vtypes( --   NB: equal vtypes can have diff validities depending
 vt_id serial primary key, -- on used product
 vt_type varchar(20));

create table vaccinations(
 vac_id serial primary key,
 vac_type int not null references vtypes,
 vac_prid int not null references products, -- used product
 vac_sid int not null references products, -- service
 vac_validity int not null references validities,
 vac_spec int not null); -- bitmask

create table vdues(vd_pid int not null references patients,vd_type int references vtypes,vd_vdue date not null);

 -- to ease use of the diverse tables, currently unused
-- create or replace view vacs (v_id,v_prod,v_serv,v_short,v_nprice,v_spec) as select vac_id,p.pr_name,s.pr_name,s.pr_short,case when s.pr_nprice=0 then 0.00 else p.pr_nprice + s.pr_nprice end,vac_spec from vaccinations,products p,products s where vac_prid=p.pr_id and vac_sid=s.pr_id;

create table symptoms(
 sy_id serial primary key,
 symptom varchar(80) not null,
 sy_short varchar(5) not null);

create table applications(
 app_id serial primary key,
 app_keyword varchar(20) not null);

create table app2prod( -- link product to service: a injectable->injection
 a2p_prid int primary key references products,
 a2p_prod int not null references applications);

/*create table withdrawals( -- wartezeiten #d
 w_id serial primary key,
 w_prid int references products,
 w_spec int references species,
 w_app int references wd_apps,
 w_meat int not null,
 w_milk int,
 w_eggs int,
 w_obs boolean not null default FALSE);

create table wd_apps( -- wd dependent on app type and/or dosage
 wda_id serial primary key,
 wda_app varchar(8),
 wda_dosage varchar(120));*/

create table invoices( -- hierwei
 inv_id serial primary key,
 inv_branch int not null default 1 references branches,
 inv_no int not null);
-- cave 0er Jahre: select length(n::text)<10 -> +0
-- wie invoicen?

create table payments(pay_id serial primary key,pay_cid int not null default 1 references clients,pay_amount numeric(9,2)not null default 0,pay_dt timestamp not null default current_timestamp,pay_mode int not null default 1 references paymodes,pay_regd date,pay_ref varchar not null default '');

create table appointments(
 app_id serial primary key,
 app_branch int not null default 1 references branches,
 app_dt timestamp not null,
 app_text varchar(128) not null,
 app_cid int references clients,
 app_pid int references patients,
 app_staffid int references staff,
 app_dur interval not null default '0:00',
 app_status char not null default 'o');

create table events(e_id serial primary key,e_pid int references patients);

create table prods(
 prod_id serial primary key,
 prod_consid int not null references events,
 prod_prid int not null references products,
 prod_count numeric(9,2) not null default 1,
 prod_dt timestamp not null,
 prod_symp int references symptoms,
 prod_staff int not null default 1 references staff);

create table clinhists(
 ch_id serial primary key,
 ch_consid int not null references events,
 ch_dt timestamp not null,
 ch_text varchar(1024),
 ch_symp int references symptoms,
 ch_staff int not null default 1 references staff);

create table accs(
 acc_id serial primary key,
 acc_branch int not null default 1 references branches,
 acc_cid int not null references clients,
 acc_prid int references prods,
 acc_npr numeric(9,2) not null,
 acc_vat int not null references vats,
 acc_inv int references invoices);

create table insts(
 in_prodid int not null primary key references prods,
 in_text varchar(300) not null default '');

create table weights(
 w_id serial primary key,
 w_pid int not null references patients,
 w_dt timestamp not null default current_timestamp,
 w_est bool not null default false,
 w_weight numeric(7,3)not null,
 w_staff int not null default 1 references staff);

create table vaccs(
 v_id serial primary key,
 v_pid int not null references patients,
 v_type int not null references vaccinations,
 v_chb varchar(30) not null default '',
 v_dt date not null); -- tolerable redundance

 -- hierwei
-- create table receipts(recpt_id serial primary key, recpt_date date not null, recpt_cid int not null references clients, recpt_sum numeric(9,2) not null, recpt_paymode varchar(30));
-- de: 'Bar', 'Kontokarte', 'Kreditkarte', 'Scheck', 'Überweisung', 'Einzug'

-- create type statem_env as enum ('Invoice','Receipt','Letter','Statement');
-- create table statements(stat_id serial primary key, stat_env statem_env not null, statement varchar(80) not null);

-- create type ordermode as enum('fax','email','modem','online','application','phone','letter'); --?
-- create table orders(ord_id serial primary key, ord_date timestamp not null, ord_prid int not null references products, ord_amount int not null, ord_supplier int not null references suppliers, ord_method ordermode not null);

-- delivery?

-- create table orderTIMESTAMP(o_id serial primary key, ono varchar(15) not null, oprid int not null references products, ogprice numeric(6,2) not null, ogvat int not null references vats, ogamount numeric(6,3) not null, ogdate date not null, osentdate date not null, ogreceived date/*?*/ not null, ogpaid date not null);

-- journals from present data.
-- archives:older 2a  waiting invoices?  receipts?
-- statistics about products/goods/services per time period
