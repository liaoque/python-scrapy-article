
import json
from pytdx.hq import TdxHq_API


def getAllGaiNaian():
    """
    取所有通达信概念
    :return:
    """
    blocknames = []
    api = TdxHq_API(auto_retry=True)
    if api.connect('124.71.187.122', 7709):
        data = api.get_and_parse_block_info("block_gn.dat")  # 返回普通list
        blocknames = map(lambda item: (item["blockname"], item["code"]), data)
        # blocknames = set(blocknames)

        api.disconnect()

    return blocknames


