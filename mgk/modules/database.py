import pymysql

_db = {
	'host': 'localhost',
	'user': 'cryart',
	'passwd': '',
	'db': 'mgk',
	'port': 3306,
	'charset': 'utf8',
	'connect_timeout': 3600,
	'autocommit': True
}

async def fetchall(query, *args, **kwargs):
    conn = pymysql.connect(**_db)
    c = conn.cursor(pymysql.cursors.DictCursor)
    c.execute(query, *args, **kwargs)
    r = c.fetchall()
    c.close()
    conn.close()
    return r

async def fetchone(query, *args, **kwargs):
    conn = pymysql.connect(**_db)
    c = conn.cursor(pymysql.cursors.DictCursor)
    c.execute(query, *args, **kwargs)
    r = c.fetchone()
    c.close()
    conn.close()
    return r

async def execute(query, *args, **kwargs):
    conn = pymysql.connect(**_db)
    c = conn.cursor(pymysql.cursors.DictCursor)
    r = c.execute(query, *args, **kwargs)
    c.close()
    conn.close()
    return r
