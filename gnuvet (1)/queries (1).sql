-- Collection of all sql statements
-- create delete insert select update
--egrep -l "[\'\"]{1}COMMAND\ " *.py
--
-- LEGEND:
-- = fits
-- X delete here -> is there
-- M move from here -> to there
-- C copy from here -> to there
-- W work nec
-- R redundant?
-- T transfer data from parent/gaia?
-- 

--ok create table weight%s(w_id serial primary key,w_est boolean not null default FALSE, w_date timestamp not null default current_timestamp,weight numeric(7,3)not null,w_staff integer references staff not null) -- weight =

create temporary table tc{}(consid integer not null,okey integer not null default 0,dt timestamp not null,type ptype not null default 'hst',txt varchar(1024)not null,count numeric(8,2)not null default 0,symp integer,unit varchar(5)not null default '',staff varchar(5),seq smallint not null,prid integer not null default 0) -- patient =

delete from appointments where app_id=%s returning app_id -- appoint =
--delete from weight%s where w_date=%s and weight=%s -- weight =
delete from weights where w_pid=%s and w_date=%s and weight=%s

--hierwei
--insert into acc{}(acc_pid,acc_prid,acc_npr,acc_vat)values(%s,%s,%s,%s)returning acc_id -- patient.book_cons =
insert into accs(acc_cid,acc_prid,acc_npr,acc_vat)values(%s,%s,%s,%s)returning acc_id
--insert into acc{}(acc_pid,acc_prid,acc_npr,acc_vat)values(%s,%s,%s,%s)returning acc_id -- patient.book_prod = dto redundant?
--insert into acc{}(acc_pid,acc_prid,acc_npr,acc_vat)values(%s,%s,%s,%s)returning acc_id -- patient.book_vac = dto redundant?

insert into addresses(housen,street,village,city,region,postcode)values(%s,%s,%s,%s,%s,%s)returning addr_id -- saecli =

insert into appointments(app_dt,app_text,app_cid,app_pid,app_staffid,app_dur,app_status)values(%s,%s,%s,%s,%s,%s,%s)returning app_id -- appoint =

insert into basecolours(bcol,bc_speccode,bc_combine)values(%1, %2, %3)returning bcol_id -- aebasecol =

insert into ch{}(consid,dt,text,symp,staff)values(%s,%s,%s,%s,%s)returning id -- patient.book_cons =
insert into ch{}(consid,dt,text,symp,staff)values(%s,%s,%s,%s,%s)returning id -- patient.book_vac =

insert into clients(c_title,c_sname,c_mname,c_fname,c_address,c_email,c_reg,c_anno)values(%s,%s,%s,%s,%s,%s,%s,%s)returning c_id -- saecli =

insert into e{} default values returning id -- patient.ck_consid =
insert into e{} default values returning id -- patient.ck_consid =

insert into inst{}(text,prodid)values(%s,%s)returning id -- patient =
insert into invoices(inv_no)values(%s)returning invoice_id -- patient M -> client
insert into neuts(neut_id,neut_date)values(%s, %s)returning neut_id -- saepat C -> patient on castr?

insert into patients(p_name,p_cid,breed,xbreed,dob,dobest,colour,sex,neutd,vicious,p_reg,p_anno,loc,identno,rip,ins)values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)returning p_id -- saepat =
insert into patients(p_name,p_cid,p_reg)values('nn',%s,%s)returning p_id -- saecli =

insert into phones values{}returning phone_cid -- saecli =

insert into prod{}(consid,dt,prodid,count,symp,staff)values(%s,%s,%s,%s,%s,%s) returning id -- patient.book_cons =
insert into prod{}(consid,dt,prodid,count,symp,staff)values(%s,%s,%s,%s,%s,%s) returning id -- patient.book_prod =
insert into prod{}(consid,dt,prodid,count,symp,staff)values(%s,%s,%s,%s,%s,%s) returning id -- patient.book_vac =

insert into tc{0}(consid,okey,dt,txt,symp,staff,seq)select consid,id,dt,text,symp,stf_short,enumsortorder from ch{0},staff,pg_enum where staff=stf_id and enumlabel::text='hst' -- patient =
insert into tc{0}(consid,okey,dt,type,txt,count,symp,staff,seq,prid,unit)select consid,id,dt,pr_type,pr_name,count,symp,stf_short,enumsortorder,pr_id,u_abbr from prod{0},products,units,staff,pg_enum where prodid=pr_id and pr_u=u_id and staff=stf_id and enumlabel::text=pr_type::text -- patient =

insert into toorder(o_prid,o_date)values(%s,%s) -- patient =
insert into vdues values(%s,%s,%s)returning vd_vdue -- patient =
insert into weight%s(w_est,w_date,weight,w_staff)values(%s, %s, %s, %s) -- weight =

select a2p_prod from app2prod where a2p_prid=%s -- patient =
select acc_pid,acc_npr,vat_rate,count from acc{0},prod{1},vats where acc_vat=vat_id and acc_prid=prod{1}.id and acc_pid=%s -- patient W acc_paid =
select addr_id from addresses where housen=%s and street=%s and village=%s and city=%s and region=%s and postcode=%s -- saecli =

select app_cid from appointments where app_id=%s -- appoint =
select app_cid, app_pid from appointments where app_id=%s -- appoint =
select app_dt,app_text,app_cid,app_pid,app_staffid,app_dur,app_status from appointments where app_id=%s -- appoint =

select app_id,app_dt,app_text,app_cid,app_pid,app_dur from appointments where app_dur!='0' and(app_dt,app_dur)overlaps(%s,%s) -- datefix =

select app_id,app_dt,app_text,app_cid,app_pid,app_staffid,app_status from appointments where app_dt between %s and %s {}order by app_dt,app_dur -- appoint =

select app_id,app_staffid,app_dt from appointments where app_staffid=%s and(date %s,interval %s)overlaps(app_dt,app_dur) -- appoint =

select app_keyword from applications where app_id=%s -- patient =
select app_pid from appointments where app_id=%s -- appoint =
select b_spec from breeds,patients where p_id=%s and breed=breed_id -- products =
select branch_name,branch_tel,housen,street,village from branches,addresses where branch_address=addr_id and branch_id=%s -- products =

select breed_id,breed_name,b_spec from breeds order by breed_name -- saepat =
select breed_id,breed_name,b_spec from breeds order by breed_name -- saepat R?

select breed_id,breed_name,b_spec from breeds where b_spec=%s order by breed_name -- saepat =

select c_id from clients where c_fname ilike %s -- saepat =
select c_id from clients where c_sname ilike %s -- saepat =
select c_id from clients where c_sname ilike %s and c_fname ilike %s -- saepat =
select c_sname from clients where c_id=%s -- appoint =
select c_sname from clients where c_id=%s -- datefix T from appoint?
select c_sname from clients where c_id=%s -- datefix T from appoint?
select c_speccode from colours where col_id=%s -- saepat =
select chr_name from chronics -- patient =
select col1,col2,col3 from colours where col_id=%s -- saepat =
select col_id from colours where col1=%s or col2=%s or col3=%s -- saepat =

select col_id from colours where(col1=%s and((col2=%s and col3=%s)or(col3=%s and col2=%s)))or(col2=%s and((col1=%s and col3=%s)or(col3=%s and col1=%s)))or(col3=%s and((col1=%s and col2=%s)or(col2=%s and col1=%s))) -- saepat =
select col_id from colours where(col1=%s and(col2=%s or col3=%s))or(col2=%s and(col1=%s or col3=%s))or(col3=%s and(col1=%s or col2=%s)) -- saepat =
select col_id,b1.bcol,b2.bcol,b3.bcol from basecolours b1,basecolours b2,basecolours b3,colours where b1.bcol_id=col1 and b2.bcol_id=col2 and b3.bcol_id=col3{} order by b1.bcol nulls first, b2.bcol nulls first, b3.bcol nulls first -- saepat =

select consid,id,dt,pr_type,pr_name,count,symp,stf_short,enumsortorder,pr_id,u_abbr from prod{0},products,units,staff,pg_enum where prodid=pr_id and pr_u=u_id and staff=stf_id and enumlabel::text=pr_type::text -- subselect -- patient =
select consid,id,dt,text,symp,stf_short,enumsortorder from ch{0},staff,pg_enum where staff=stf_id and enumlabel::text='hst' -- subselect -- patient =

select count(*)from pg_tables where tablename='weight%s' -- weight =
select count(id) from ch{} where consid=%s -- patient =
select count(id) from prod{} where consid=%s -- patient =

select distinct breed_id,breed_name,b_spec from breeds,species where spec_id=b_spec{} order by breed_name -- saepat =

select distinct c_fname from clients order by c_fname -- saecli =
select distinct c_fname from clients order by c_fname -- saepat =
select distinct c_mname from clients order by c_mname -- saecli =
select distinct c_sname from clients order by c_sname -- saecli =
select distinct c_sname from clients order by c_sname -- saepat =
select distinct city from addresses order by city -- saecli =
select distinct housen from addresses order by housen -- saecli =
select distinct identno from patients where identno is not null order by identno -- saepat =
select distinct p_name from patients order by p_name -- saecli =
select distinct p_name from patients order by p_name -- saepat =

select distinct petpass from patients where petpass is not null order by petpass -- saepat =
select distinct postcode from addresses order by postcode -- saecli =
select distinct region from addresses order by region -- saecli =
select distinct street from addresses order by street -- saecli =
select distinct village from addresses order by village -- saecli =

select dt,txt,count,unit,symp,staff,consid,okey,type,prid from tc{0} order by dt,seq -- patient =
select enum_range(null::ptype) -- patient =
select housen,street,village,city,region,postcode,l_tel,l_mobile from locations,addresses where l_address=addr_id and l_id=%s -- patient =
select i_name,i_id from insurances order by i_name -- saepat =
select i_name,i_rep,housen,street,village,city,region,postcode,i_tel,i_email,i_anno from insurances,addresses where i_address=addr.id and i_id=%s -- patient =
select inst_id,inst_pos,inst_txt,inst_abbr from instructions order by inst_pos,inst_txt -- products =
select l_id,l_name,housen,street from locations,addresses where l_address=addr_id order by l_name,housen,street -- saepat =

select m_id,m_name,m_rate from markups where not m_obs -- patient =
select m_id,m_name,m_rate from markups where not m_obs -- products =

select max(dt)from ch{} where consid=%s -- patient =
select max(dt)from prod{} where consid=%s -- patient =
select max(id)from ch{} -- patient =
select max(id)from e{} -- patient =
select max(id)from prod{} -- patient =
select max(inv_no)from invoices -- patient M -> client
select min(dt),max(dt)from prod{} where consid=%s -- patient =

select neut_date from neuts where neut_id=%s -- saepat =
select neut_id,neut_date from neuts where neut_id=%s -- saepat.ck_neutdate =
select neut_id,neut_date from neuts where neut_id=%s -- saepat.pat_edit =

select nh_pid,nh_name,nh_date from namehistory where nh_name ilike %s -- saepat =

select p_id from patients where identno=%s -- saepat =
select p_id from patients where p_cid=%s -- patient =
select p_id from patients where p_name=%s and p_cid=%s and not rip -- saepat =
select p_id from patients where p_name=%s and p_cid=%s and not rip and p_id!=%s -- saepat =

select p_name from patients where p_id=%s -- appoint =
select p_name from patients where p_id=%s -- weight T from patient?

select p_name,breed,xbreed,colour,sex,neutd,vicious,rip,identno,petpass,p_anno,dob,dobest,loc,p_reg,ins,p_last,chr,c_id,c_surname,c_forename from patients,clients where p_cid=c_id and p_id=%s -- saepat =
select p_name,breed,xbreed,dob,dobest,colour,sex,neutd,vicious,identno,p_reg,p_anno,loc,ins,rip,t_title,c_sname,c_mname,c_fname from patients,clients,titles where p_id=%s and p_cid=c_id and c_title=t_id -- saepat =

select p_name,p_cid from patients where p_id=%s -- datefix =

select p_name,xbreed,breed_abbr,breed_name,sex,neutd,case when b1.bcol is not null then b1.bcol else '' end||case when b2.bcol is not null then '-'||b2.bcol else '' end||case when b3.bcol is not null then '-'||b3.bcol else '' end,dob,dobest,vicious,rip from patients,breeds,colours,basecolours b1,basecolours b2,basecolours b3 where p_cid=%s and breed=breed_id and colour=col_id and b1.bcol_id=col1 and b2.bcol_id=col2 and b3.bcol_id=col3 order by p_name -- client =
select p_name,xbreed,breed_name,sex,neutd,dob,dobest,vicious,rip,b1.bcol,b2.bcol,b3.bcol,l_id,l_name,p_anno,p_cid,t_title,c_sname,c_fname,baddebt,housen,street,village,city,postcode,chr,identno,petpass,ins,p_last from patients,breeds,clients,colours,addresses,titles,basecolours b1,basecolours b2,basecolours b3,locations where p_id=%s and p_cid=c_id and breed=breed_id and colour=col_id and b1.bcol_id=col1 and b2.bcol_id=col2 and b3.bcol_id=col3 and c_title=t_id and c_address=addr_id and loc=l_id -- patient =

select phone_num,phone_anno from phones where phone_clid=%s order by phone_opt -- client =
select phone_opt,phone_num,phone_anno from phones where phone_clid=%s order by phone_opt -- patient =

select pr_limit from products where pr_id=%s -- patient =
select pr_name from products where pr_id=%s -- patient =

select pr_name,pr_short,pr_u,pr_nprice,pr_vat,pr_id,pr_type,pr_instr from products,vats,vaccinations where not pr_obs and pr_vat=vat_id and pr_type=%s and vac_sid=pr_id and vac_spec=%s {}order by pr_name -- products.list_cons =
select pr_name,pr_short,pr_u,pr_nprice,vat_id,pr_id,pr_type,pr_instr from products,vats where not pr_obs and pr_vat=vat_id and pr_type=%s {}order by pr_name -- products.list_goods =
select pr_name,pr_short,pr_u,pr_nprice,vat_id,pr_id,pr_type,pr_instr from products,vats where not pr_obs and {0} ilike %s and pr_vat=vat_id and pr_type in(%s,%s)order by {0} -- products.list_prod =
select pr_name,pr_short,pr_u,pr_nprice,vat_id,pr_id,pr_type,pr_instr from products,vats where not pr_obs and {0} {1} %s and pr_vat=vat_id and pr_type not in(%s,%s)order by {0} -- products.list_vaccs =

select pr_name,pr_u from products where pr_id=%s -- patient.book_prod =
select pr_name,pr_u from products where pr_id=%s -- patient.book_vac =

select pr_stock from products where pr_id=%s -- patient.book_prod =
select pr_stock from products where pr_id=%s -- patient.book_vac =

select rip_date from rips where rip_id=%s -- patient =

select seen_pid from seen where seen_date=%s -- saepat =

select spec_id,spec_name from species order by spec_name -- saepat =
select spec_name,spec_id,spec_code from species order by spec_name -- aebasecol =
select stf_func,stf_id from staff where stf_logname=%s -- gnuv =

select stf_id,stf_short from staff order by stf_id -- appoint =
select stf_id,stf_short from staff order by stf_short -- datefix =

select stf_logname from staff where stf_id=%s -- appoint T from gaia?
select stf_logname from staff where stf_id=%s -- appoint T from gaia?
select stf_logname from staff where stf_id=%s -- client T from gaia?
select stf_logname from staff where stf_id=%s -- patient T from gaia?
select stf_logname from staff where stf_id=%s -- products T from gaia?
select stf_logname from staff where stf_id=%s -- saecli T from gaia?
select stf_logname from staff where stf_id=%s -- saepat T from gaia?
select stf_logname from staff where stf_id=%s -- weight T from gaia?

select stf_short from staff where stf_id=%s -- patient T from gaia?

select sum(acc_npr*(1+vat_rate))from acc{},vats where acc_vat=vat_id -- client W =
select sum(acc_npr*(1+vat_rate)-(select sum(pay_amount)from pay{0})from acc{0} where acc_vat=vat_id -- client =

select sy_id,symptom,sy_short from symptoms order by symptom -- patient =
select sy_id,symptom,sy_short from symptoms order by symptom -- products =

select t_id,t_title from titles order by t_id -- saecli =
select t_title,c_sname,c_fname,c_mname from clients,titles where c_title=t_id and c_id=%s -- saepat =
select t_title,c_sname,c_mname,c_fname,housen,street,village,city,region,postcode,c_email,baddebt,c_reg,c_last,c_anno from clients,titles,addresses where t_id=c_title and c_address=addr_id and c_id=%s -- client =

--select tablename from pg_tables where tablename like 'pay{}' -- client M -> saecli
select tablename from pg_tables where tablename='acc{}' -- patient X -> saecli
select tablename from pg_tables where tablename='acc{}' -- saecli
select tablename from pg_tables where tablename='ch{}' -- patient
select tablename from pg_tables where tablename='e{}' -- patient M -> saecli
select tablename from pg_tables where tablename='inv{}' -- patient M -> client
select tablename from pg_tables where tablename='prod{}' -- patient M -> saecli
select tablename from pg_tables where tablename='prod{}' -- patient M -> saecli
select tablename from pg_tables where tablename='weight%s' -- patient =

--select text from inst{} where prodid=%s -- patient =
select in_text from insts where in_prodid=%s -- patient

select u_id,u_name,u_pl,u_short from units -- products =
select u_id,u_name,u_pl,u_short,u_abbr from units -- patient =

select vac_prid from vaccinations where vac_sid=%s -- patient =
select vac_type,val_days from vaccinations,validities where vac_validity=val_id and vac_sid=%s -- patient =

select vat_id,vat_name,vat_rate from vats where not vat_obs -- patient =
select vat_id,vat_name,vat_rate from vats where not vat_obs -- products =

select vd_pid,vt_type from vdues,vtypes,patients where vt_id=vd_type and vd_pid=p_id and not rip and vd_vdue<%s -- gnuv =
select vd_type from vdues where vd_pid=%s -- patient =
select vt_type,vd_vdue from vdues,vtypes where vd_type=vt_id and vd_pid=%s -- patient =

select w_date,weight,w_est,w_staff from weight%s order by w_date -- weight =
select weight,w_date,w_est from weight%s order by w_date desc limit 1 -- patient =

update appointments set app_dt=%s,app_text=%s,app_cid=%s,app_pid=%s,app_staffid=%s,app_dur=%s,app_status=%s where app_id=%s returning app_id -- appoint =

update appointments set app_status=%s where app_id=%s returning app_id -- appoint =
update appointments set app_status=%s where app_id=%s returning app_id -- appoint =
update appointments set app_status=%s where app_id=%s returning app_id -- appoint =

update neuts set neut_date=%s where neut_id=%s returning neut_id -- saepat =

update patients set p_name=%s,breed=%s,xbreed=%s,dob=%s,dobest=%s,colour=%s,sex=%s,rip=%s,vicious=%s,identno=%s,p_reg=%s,p_anno=%s,loc=%s,ins=%s,neutd=%s where p_id=%s returning p_id -- saepat =

update products set pr_stock=pr_stock-%s where pr_id=%s returning pr_stock -- patient =
update products set pr_stock=pr_stock-%s where pr_id=%s returning pr_stock -- patient R ?

update vdues set vd_vdue=%s where vd_pid=%s and vd_type=%s returning vd_vdue -- patient =
