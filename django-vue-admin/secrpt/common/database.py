
database_config = {
    'default' : {
        "uri" :  'mongodb://localhost:27017/',
        "db_name": "stock_db",
        # 'limitup_records' :"limitup_records"
    },
    'mysql' :{
        'host' :"127.0.0.1",
        'user' :"qingxu",
        'passwd' :"t5Nw83MHn2sbsJBW",
        'db' :"qingxu",
    }
}

def getConfig(key):
    return  database_config[key]