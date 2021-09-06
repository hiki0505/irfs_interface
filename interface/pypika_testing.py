# from pypika import Query, Table, Field
#
# q = Query.from_('customers').select('id', 'fname', 'lname', 'phone')
#
# print(str(q))
#
# from pypika import Table, Query
#
# customers = Table('customers')
# q = Query.from_(customers).select(customers.id, customers.fname, customers.lname, customers.phone)
#
# print(str(q))
from sqlalchemy import create_engine, MetaData, Table
from sqlalchemy.sql import select
import pandas as pd
# engine = create_engine('sqlite:///:memory:', echo=True)

engine = create_engine('oracle+cx_oracle://hikmat_pirmammadov:hikmat07@192.168.0.17:1521/?service_name=bank', echo=True)
connection = engine.connect()
metadata = MetaData(bind=engine)
my_table = Table('SQLALCHEMY_DATA', metadata, autoload=True)
# s = select(my_table)
# print(s)


# result = connection.execute(s)
# for row in result:
#     print(row)
p0 = 'select * from'

# x1 = (
#     select(["t0.{repd}, count(t0.acc) as orig_count, sum(t0.amt) as orig_amount, sum(nvl(t3.deft,0))/count(t0.acc)".format(repd='repd')])
# )

x1 = select(my_table.c.filial)


print(x1)
