import configparser

# 创建ConfigParser对象
config = configparser.ConfigParser()

# 读取INI文件
config.read('config.ini')


def getConfig():
    return config


def saveDefault(k, v):
    config["DEFAULT"][k] = v
    # 写入到新的INI文件
    with open('config.ini', 'w') as configfile:
        config.write(configfile)


def checkDefault(k):
    return config["DEFAULT"][k] == "0"

