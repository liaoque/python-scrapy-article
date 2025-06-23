
database_config = {
    'default' : {
        "uri" :  'mongodb://localhost:27017/',
        "db_name": "stock_db",
        # 'limitup_records' :"limitup_records"
    },
    'mysql' :{
        'host' :"",
        'user' :"",
        'passwd' :"",
        'db' :"qingxu",
    }
}

def getConfig(key):
    return  database_config[key]