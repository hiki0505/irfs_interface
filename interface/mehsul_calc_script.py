import cx_Oracle as co
from .config import database_table_name_caps, database_table_name
import pandas as pd


def mehsul_adding(db_credentials, plist_globs):
    conn = co.connect(u'{}/{}@{}/{}'.format(db_credentials['username'], db_credentials['password'], db_credentials['host'], db_credentials['dbname']))
    # conn = co.connect(
    #     u'{}/{}@{}/{}'.format(db_credentials.username, db_credentials.password, db_credentials.host,
    #                           db_credentials.dbname))
    cursor = conn.cursor()
    # sql_init = 'ALTER TABLE portfolio_test2 ADD mehsul VARCHAR(255)'
    # cursor.execute(sql_init)
    # conn.commit()
    #
    # sql_code = 'UPDATE ruqiyye_bedirova.portfolio_test2 SET mehsul = case '
    # for i, j in plist_globs.items():
    #     sql_code += "when fea_kodu in {plist} then '{prod_name}' ".format(plist=j, prod_name=i)
    #
    # sql_code += "else 'none' end"
    #
    # cursor.execute(sql_code)
    # conn.commit()




    sql_code = '''DECLARE
                  v_column_exists INTEGER;  
                BEGIN
                  SELECT count(*) into v_column_exists
                  FROM all_tab_columns 
                  WHERE table_name = '{}' AND column_name = 'MEHSUL';
                
                  if (v_column_exists) = 1
                  then
                      NULL;
                  else
                      execute immediate 'ALTER TABLE {} ADD mehsul VARCHAR(255)';
                      execute immediate 'UPDATE {}
                                            SET mehsul = case '''.format(database_table_name_caps, database_table_name, database_table_name)
    for i, j in plist_globs.items():
        plist = j.replace("'", "''")
        sql_code += "when fea_kodu in {plist} then ''{prod_name}'' ".format(plist=plist, prod_name=i)
        # sql_code += "when fea_kodu in {plist} then '{prod_name}' ".format(plist=j, prod_name=i)

    sql_code += '''else ''cards''
                   end';
                commit;
            end if;
        end;'''

    print(sql_code)
    cursor.execute(sql_code)


    final_query = 'SELECT * FROM {} order by act_date'.format(database_table_name_caps)
    portfolio = pd.read_sql(final_query, conn)

    conn.close()
    return portfolio


# PLIST_GLOBS = {
#     'consumer': "(01801, 02201, 02203, 02800, 02801, 02803, 02805)",
#     'corporate': "(01821, 01803, 01805, 01806, 01807, 01808, 01855, 01856, 01857, 01858, 02002, 02004, 02009, 02014, 02017, 02100, 02102, 02103, 02201, 02203, 02300, 02304, 02400, 02600) and must_novu not like 'F%Z%K%'",
#     'sole': "(01821, 01803, 01805, 01806, 01807, 01808, 01855, 01856, 01857, 01858, 02002, 02004, 02009, 02014, 02017, 02100, 02102, 02103, 02300, 02304, 02400, 02600) and must_novu like 'F%Z%K%'"
# }
#
# db_credentials = {'engine': 'on', 'username': 'ruqiyye_bedirova', 'password': 'ruqiyye03', 'host': '192.168.0.17', 'dbname': 'bank'}
#
#
# mehsul_adding(db_credentials, PLIST_GLOBS)


# '''
# DECLARE
#           v_column_exists INTEGER;
#         BEGIN
#           SELECT count(*) into v_column_exists
#           FROM all_tab_columns
#           WHERE table_name = 'PORTFOLIO_TEST2' AND column_name = 'EAD_LINE';
#
#           if (v_column_exists) = 1
#           then
#               NULL;
#           else
#               execute immediate 'ALTER TABLE portfolio_test2 ADD ead_line NUMBER(38,2)';
#               execute immediate 'UPDATE portfolio_test2
#                                     SET ead_line = case when fea_kodu in {{ prod_cards }} then {calc} else 0
#            end';
#         commit;
#     end if;
# end;
# '''


# def ead_line_adding(db_credentials, plist_globs):
#     conn = co.connect(
#         u'{}/{}@{}/{}'.format(db_credentials['username'], db_credentials['password'], db_credentials['host'],
#                               db_credentials['dbname']))
#     cursor = conn.cursor()