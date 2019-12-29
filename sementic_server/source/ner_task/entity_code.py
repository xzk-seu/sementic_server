"""
@description: 与知识库对应的实体编码表
@author: Cui Rui long
@email: xiaocuikindle@163.com
@time: 2019-02-27
@version: 0.0.1
"""

import yaml
import os


class EntityCode(object):
    """实体名称及编码类"""

    def __init__(self):

        self.account = ['qq_num', 'mob_num', 'phone_num', 'idcard_value', 'email_value', 'wechat_value', 'qq_group_num',
                        'wx_group_num', 'alipay_valu', 'douyin_value', 'jd_value', 'taobao_value', 'microblog_value',
                        'vehcard_value', 'imei_value', 'mac_value', 'unlabel']

        self.ner_entities_dics = {'NAME': 'NAME', 'COMPANY': 'CPNY_NAME', 'ADDR': 'ADDR_VALUE', 'DATE': 'DATE'}
        rootpath = str(os.getcwd()).replace("\\", "/")
        if 'source' in rootpath.split('/'):
            f_r = open(os.path.join(os.getcwd(), os.path.pardir, os.path.pardir, 'data', 'yml', 'node_code.yml'),
                       encoding='utf-8')
        else:
            f_r = open(os.path.join(os.getcwd(), 'sementic_server', 'data', 'yml', 'node_code.yml'), encoding='utf-8')

        self.entities_code = yaml.load(f_r, Loader=yaml.SafeLoader)
        self.account_label = {"EMAIL": "email_value",
                              "MPHONE": "mob_num",
                              "PHONE": "phone_num",
                              "QQ": "qq_num",
                              "QQ_GROUP": "qq_group_num",
                              "WX_GROUP": "wx_group_num",
                              "WECHAT": "wechat_value",
                              "ID": "idcard_value",
                              "MBLOG": "microblog_value",
                              "ALIPAY": "alipay_value",
                              "DOUYIN": "douyin_value",
                              "TAOBAO": "taobao_value",
                              "JD": "jd_value",
                              'IMEI': 'imei_value',
                              "UNLABEL": "unlabel"}

        self.punctuation = [',', '，', '~', '!', '！', '。', '.', '?', '？']

    def get_account(self):
        return self.account

    def get_ner_entities(self):
        return self.ner_entities_dics

    def get_entities(self):
        return list(self.ner_entities_dics.values()) + self.account

    def is_account(self, account):
        if account in self.account:
            return True
        else:
            return False

    def get_entity_code(self):
        return self.entities_code

    def get_account_label(self):
        return self.account_label
