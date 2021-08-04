# from .services import db_connection

# conn = db_connection('oracle', 'ruqiyye_bedirova', 'ruqiyye03', '192.168.0.17', 'Naxchivan_R')
# print(conn)
import cx_Oracle as co
conn_str = 'ruqiyye_bedirova/ruqiyye03@192.168.0.17:1521/bank'
conn = co.connect(conn_str)

cur = conn.cursor()

cur.execute('''
DECLARE
CURSOR cur 
IS
    SELECT loss, id, product 
    FROM new_los;
    maxloss NUMBER(38,7);
    product_ VARCHAR(500);
    loss_ NUMBER(38,7);
    id_ NUMBER(38,7);
BEGIN
OPEN cur;
LOOP
FETCH cur INTO loss_, id_, product_;
IF cur%NOTFOUND
THEN
EXIT;
END IF;

IF id_ = 1 THEN
    maxloss := loss_;
ElSE
    IF loss_ > maxloss
    THEN
        maxloss := loss_;
    ELSE maxloss := maxloss;
    END IF;
END IF;
UPDATE new_los SET cl = maxloss WHERE id = id_ and product = product_;

END LOOP;
CLOSE cur;
END;
/
''')


# print(conn)