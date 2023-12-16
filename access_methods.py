from sqlite3 import *

def IIf(chk, true_case, false_case=None):
	if chk: return true_case
	else: return false_case

def Nz(val, nul_case=0):
	if val == None: return nul_case
	else: return val

# return a list of dictionaries from a db query
# need the connection. Is inherent in DAO.Database
# Read only
def OpenRecordset(con, qry_sql, param=None):
	cur = con.cursor()
	rst = []
	k = []
	
	if param != None: res = cur.execute(qry_sql, param)
	else: res = cur.execute(qry_sql)
	
	for desc in cur.description: k.append(desc[0])
	
	for row in res.fetchall(): rst.append(dict(zip(k,row)))
	
	cur = None
	return rst