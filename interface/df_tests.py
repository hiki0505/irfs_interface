# from pypika import Case, Tables, Query, functions as fn
#
# PLIST_GLOBS = {
#     'consumer': "(01801, 02201, 02203, 02800, 02801, 02803, 02805)",
#     'corporate': "(01821, 01803, 01805, 01806, 01807, 01808, 01855, 01856, 01857, 01858, 02002, 02004, 02009, 02014, 02017, 02100, 02102, 02103, 02201, 02203, 02300, 02304, 02400, 02600) and must_novu not like 'F%Z%K%'",
#     'sole': "(01821, 01803, 01805, 01806, 01807, 01808, 01855, 01856, 01857, 01858, 02002, 02004, 02009, 02014, 02017, 02100, 02102, 02103, 02300, 02304, 02400, 02600) and must_novu like 'F%Z%K%'"
# }
#
# '''
# SELECT RUQIYYE_BEDIROVA.portfolio_test2.*,
#     case
#         when fea_kodu in (01821, 01803, 01805, 01806, 01807, 01808, 01855, 01856, 01857, 01858, 02002,
#         02004, 02009, 02014, 02017, 02100, 02102, 02103, 02201, 02203, 02300, 02304, 02400, 02600) and must_novu not like 'F%Z%K%'
#         then 'corporate'
#         else 'sole'
#         end as mehsul FROM RUQIYYE_BEDIROVA.portfolio_test2
# '''
#
# '''
# DECLARE
#   v_column_exists INTEGER;
# BEGIN
#   SELECT count(*) into v_column_exists
#   FROM all_tab_columns
#   WHERE table_name = 'PORTFOLIO_TEST2' AND column_name = 'MEHSUL';
#       --and owner = 'SCOTT --*might be required if you are using all/dba views
#
#   if (v_column_exists = 0)
#   then
#       execute immediate 'UPDATE ruqiyye_bedirova.portfolio_test2
#                         SET mehsul =    case
#                         when fea_kodu in (01821, 01803, 01805, 01806, 01807, 01808, 01855, 01856, 01857, 01858, 02002,
#                         02004, 02009, 02014, 02017, 02100, 02102, 02103, 02201, 02203, 02300, 02304, 02400, 02600) and must_novu not like "F%Z%K%"
#                         then "corporate"
#                         else "sole"
#                         end';
#       commit;
#   else
#       execute immediate 'alter table ruqiyye_bedirova.portfolio_test2 drop column mehsul';
#       commit;
#   end if;
# end;
# '''
#
#
# # sql_code = 'INSERT INTO SELECT RUQIYYE_BEDIROVA.portfolio_test2 VALUESS'
# sql_code = '''DECLARE
#               v_column_exists INTEGER;
#             BEGIN
#               SELECT count(*) into v_column_exists
#               FROM all_tab_columns
#               WHERE table_name = 'PORTFOLIO_TEST2' AND column_name = 'MEHSUL';
#                   --and owner = 'SCOTT --*might be required if you are using all/dba views
#
#               if (v_column_exists = 0)
#               then
#                   execute immediate 'UPDATE ruqiyye_bedirova.portfolio_test2
#                                     SET mehsul = case '''
# for i, j in PLIST_GLOBS.items():
#     sql_code += "when fea_kodu in {plist} then '{prod_name}' ".format(plist=j, prod_name=i)
#     # sql_code += "when fea_kodu in {plist} then '{prod_name}' ".format(plist=j, prod_name=i)
#
# sql_code += '''else "consumer" end';
#                   commit;
#               else
#                   execute immediate 'alter table ruqiyye_bedirova.portfolio_test2 drop column mehsul';
#                   commit;
#               end if;
#             end;'''
#
# print(sql_code)

PLIST_GLOBS = {
    'consumer': "(01801, 02201, 02203, 02800, 02801, 02803, 02805)",
    'corporate': "(01821, 01803, 01805, 01806, 01807, 01808, 01855, 01856, 01857, 01858, 02002, 02004, 02009, 02014, 02017, 02100, 02102, 02103, 02201, 02203, 02300, 02304, 02400, 02600) and must_novu not like 'F%Z%K%'",
    'sole': "(01821, 01803, 01805, 01806, 01807, 01808, 01855, 01856, 01857, 01858, 02002, 02004, 02009, 02014, 02017, 02100, 02102, 02103, 02300, 02304, 02400, 02600) and must_novu like 'F%Z%K%'"
}

import cx_Oracle as co
conn_str = 'ruqiyye_bedirova/ruqiyye03@192.168.0.17:1521/bank'
conn = co.connect(conn_str)
print(conn)
cur = conn.cursor()
print(cur)

sql_code = '''DECLARE
v_column_exists INTEGER;  
BEGIN
SELECT count(*) into v_column_exists
FROM all_tab_columns 
WHERE table_name = 'PORTFOLIO_TEST2' AND column_name = 'MEHSUL';

if (v_column_exists) = 1
then
  NULL;
else
  execute immediate 'ALTER TABLE portfolio_test2 ADD mehsul VARCHAR(255)';
  execute immediate 'UPDATE portfolio_test2
                        SET mehsul = case '''
for i, j in PLIST_GLOBS.items():
    plist = j.replace("'", "''")
    sql_code += "when fea_kodu in {plist} then ''{prod_name}'' \n".format(plist=plist, prod_name=i)
    # sql_code += "when fea_kodu in {plist} then '{prod_name}' ".format(plist=j, prod_name=i)

sql_code += '''else ''none''
                   end';
                commit;
            end if;
        end;'''

print(sql_code)
cur.execute(sql_code)