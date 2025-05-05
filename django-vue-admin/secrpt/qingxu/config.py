import configparser
import os

current_dir = os.path.dirname(os.path.abspath(__file__))
# 创建ConfigParser对象
config = configparser.ConfigParser()

# 读取INI文件
d = config.read(current_dir+'/config.ini')


def getConfig():
    return config


def saveDefault(k, v):
    config["DEFAULT"][k] = v
    # 写入到新的INI文件
    with open('config.ini', 'w') as configfile:
        config.write(configfile)


def checkDefault(k):
    return config["DEFAULT"][k] == "0"

