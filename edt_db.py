from sqlite3 import *

con = connect('games.db')
cur = con.cursor()

qry_sql = """ALTER TABLE machines
ADD export_alg_res Integer"""
cur.execute(qry_sql)

con.commit()
con.close()
con = None
cur = None