from sementic_server.source.tool.global_object import semantic, account, vp_matcher, item_matcher, dep_analyzer
from sementic_server.source.tool.logger import logger


class Mention(object):
    def __init__(self, m_dict):
        self.idx = m_dict['id']
        self.mention_type = m_dict['type']
        self.content = m_dict['content']
        self.begin = m_dict['content']['begin']
        self.end = m_dict['content']['end']
        self.small_type = m_dict['content']['type']


class MentionCollector(object):
    """
    三类mention：实体、关系、值属性

    """

    def __init__(self, sentence):
        self.mentions = list()
        account_info = account.get_account_labels_info(sentence)
        intent = item_matcher.match(sentence, accounts_info=account_info)
        result, _ = semantic.sentence_ner_entities(intent)
        self.entity = result.get('entity')
        self.entity_check()
        self.entity.extend(result.get('accounts'))
        self.relation = result.get('relation')
        self.value_props = vp_matcher.match(sentence)
        self.scope_correction()
        self.relation_filter()

        self.set_mentions(self.entity, 'entity')
        self.set_mentions(self.relation, 'relation')
        self.set_mentions(self.value_props, 'entity')

        if len(result.get("entity") + result.get("accounts")) == 0:
            logger.error(sentence + "\t实体识别模块返回空值")

    def scope_correction(self):
        """
        修正begin和end值
        :return:
        """
        for e in self.entity:
            e_len = len(e['value'])
            e['end'] = e['begin'] + e_len - 1
        for e in self.relation:
            e_len = len(e['value'])
            e['end'] = e['begin'] + e_len - 1
        for e in self.value_props:
            e_len = len(e['value'])
            e['end'] = e['begin'] + e_len - 1

    def entity_check(self):
        """
        检查当前实体是否与后续实体构成一个：
        姓+名
        姓+称谓
        姓+名+称谓
        :return:
        """
        person_types = ['FIRSTNAME', 'LASTNAME', 'CHENWEI', 'PERSON']
        self.entity = sorted(self.entity, key=lambda x: x['begin'])
        new_entity = list()
        e1 = self.entity[0]
        for e2 in self.entity[1:]:
            if e2['type'] in person_types and e1['type'] in person_types:
                if check_entity_continuous(e1, e2):
                    ent = merge_entity(e1, e2)
                    e1 = ent
                else:
                    new_entity.append(e1)
                    e1 = e2
            else:
                new_entity.append(e1)
                e1 = e2
        new_entity.append(e1)
        self.entity = new_entity

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
        m_list = list()
        for m in self.mentions:
            m_list.append(Mention(m))
        return m_list

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


def check_entity_continuous(e1, e2):
    """
    判断两个实体是否连续
    :param e1:
    :param e2:
    :return:
    """
    if e1['end'] == e2['begin'] - 1:
        return True
    else:
        return False


def merge_entity(e1, e2):
    """
    合并一组实体
    """
    r_entity = dict()
    r_entity['type'] = 'PERSON'
    r_entity['value'] = e1['value'] + e2['value']
    r_entity['code'] = e1['code']
    r_entity['begin'] = e1['begin']
    r_entity['end'] = e2['end']
    detail = e1.setdefault('detail', None)
    if detail:
        detail.append(e2)
        r_entity['detail'] = detail
    else:
        r_entity['detail'] = [e1, e2]
    return r_entity


def main():
    sentence = "东南大学汪鹏老师的学生张三"
    m_collector = MentionCollector(sentence)

    for m in m_collector.mentions:
        print(m)

    deps = dep_analyzer.get_result(sentence)
    for d in deps:
        print(d)


if __name__ == '__main__':
    main()
