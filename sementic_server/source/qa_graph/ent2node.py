"""
@description: 实体类型翻译为节点类型
@author: Xu Zhongkai
@email: 1399350807@qq.com
@time: 2019-12-23
@version: 0.0.1
"""
from sementic_server.source.tool.logger import logger


def get_node_type(entity_type):
    account_list = ['QQ_NUM', 'MOB_NUM', 'PHONE_NUM', 'IDCARD_VALUE', 'EMAIL_VALUE', 'WECHAT_VALUE', 'QQ_GROUP_NUM',
                    'WX_GROUP_NUM', 'ALIPAY_VALUE', 'DOUYIN_VALUE', 'JD_VALUE', 'TAOBAO_VALUE', 'MICROBLOG_VALUE',
                    'UNLABEL', 'VEHCARD_VALUE', 'IMEI_VALUE', 'MAC_VALUE']
    """
    # ner_entities_dics = {'NAME': 'NAME', 'COMPANY': 'CPNY_NAME', 'ADDR': 'ADDR_VALUE', 'DATE': 'DATE'}
    """
    person_types = ['FIRSTNAME', 'LASTNAME', 'CHENWEI', 'PERSON']

    account_name_list = ['QQ', 'MobileNum', 'FixedPhone', 'Idcard', 'Email', 'WeChat', 'QQGroup',
                         'WeChatGroup', 'Alipay', 'DouYin', 'JD', 'TaoBao', 'MicroBlog', 'UNLABEL',
                         'VehicleCard', 'IMEI', 'MAC']

    if entity_type in account_list:
        index = account_list.index(entity_type)
        return account_name_list[index]
    elif entity_type in person_types:
        return 'Person'
    elif entity_type == 'CPNY_NAME':
        return 'Company'
    elif entity_type == 'ADDR_VALUE':
        return 'Addr'
    else:
        logger.info('Unknown type: %s' % entity_type)
        return None
