from sementic_server.source.tool.global_object import semantic, account, vp_matcher, item_matcher,logger


class MentionCollector(object):
    """
    三类mention：实体、关系、值属性
    """
    def __init__(self, sentence):
        self.mentions = list()
        account_info = account.get_account_labels_info(sentence)
        intent = item_matcher.match(sentence, accounts_info=account_info)
        result, _ = semantic.sentence_ner_entities(intent)
        self.entity = result.get('entity') + result.get('accounts')
        self.relation = result.get('relation')
        self.value_props = vp_matcher.match(sentence)
        self.relation_filter()

        self.set_mentions(self.entity, 'entity')
        self.set_mentions(self.relation, 'relation')
        self.set_mentions(self.value_props, 'entity')

        if len(result.get("entity") + result.get("accounts")) == 0:
            logger.error(sentence+"\t实体识别模块返回空值")

    def set_mentions(self, mentions, t_type):
        """

        :param mentions:
        :param t_type:
        :return:
        """
        start_id = len(self.mentions)
        for m in mentions:
            self.mentions.append({'id': start_id, 'type': t_type, 'value': m['value'], 'content': m})
            start_id += 1

    def get_mentions(self):
        return self.mentions

    def relation_filter(self):
        """
        对账号进行过滤，如果实体中出现QQ实体，则在关系中过滤ChasQQ关系
        :return:
        """
        account_dict = {'QQ_NUM': ['ChasQQ', 'PhasQQ'],
                        'MOB_NUM': ['PhasMobileNum', 'ChasMobileNum'],
                        'EMAIL_VALUE': ['PhasEmail'],
                        'WECHAT_VALUE': ['PhasWeChat'],
                        'ALIPAY_VALUE': ['PhasAlipay'],
                        'DOUYIN_VALUE': ['PhasDouYin'],
                        'JD_VALUE': ['PhasJD'],
                        'TAOBAO_VALUE': ['PhasTaoBao'],
                        'MICROBLOG_VALUE': ['PhasMicroBlog'],
                        'VEHCARD_VALUE': ['PhasVehicleCard'],
                        'IDCARD_VALUE': ['PhasIdcard'],
                        'WX_GROUP_NUM': ['PhasWeChat']}
        for e in self.entity:
            if e['type'] in account_dict.keys():
                for rel_name in account_dict[e['type']]:
                    new_relation = [x for x in self.relation if x['type'] != rel_name]
                    self.relation = new_relation


def main():
    sentence = "微信帐户DonDdon担任什么群的群主"
    m_collector = MentionCollector(sentence)

    mentions = m_collector.get_mentions()
    for m in mentions:
        print(m)


if __name__ == '__main__':
    main()
