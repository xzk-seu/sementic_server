"""
@description: 对所有mention进行集中处理
@author: Xu Zhongkai
@email: 1399350807@qq.com
@time: 2019-12-26
@version: 0.0.1
"""

from sementic_server.source.tool.global_object import semantic, account, vp_matcher, item_matcher, dep_analyzer
from sementic_server.source.tool.logger import logger


class Mention(object):
    """
    三类mention的抽象结构：实体、关系、值属性
    """
    def __init__(self, m_dict):
        self.idx = m_dict['id']
        self.mention_type = m_dict['type']
        self.content = m_dict['content']
        self.value = m_dict['content']['value']
        self.begin = m_dict['content']['begin']
        self.end = m_dict['content']['end']
        self.small_type = m_dict['content']['type']


class MentionCollector(object):
    """
    三类mention集成：实体、关系、值属性
    self.mentions以dict结构存储mention
    self.get_mentions(self)获取Mention对象
    self.scope_correction()对三类mention的下标进行统一计算
    self.entity_check()检查当前实体是否与后续实体构成一个['firstname', 'lastname', 'chenwei', 'person']
    self.relation_filter()对账号进行过滤，如果实体中出现QQ实体，则在关系中过滤ChasQQ关系，放弃
    self.relation_or_entity(self):根据下标判断一个mention是实体还是关系
    """

    def __init__(self, sentence):
        self.mentions = list()
        account_info = account.get_account_labels_info(sentence)
        intent = item_matcher.match(sentence, accounts_info=account_info)
        result, _ = semantic.sentence_ner_entities(intent)
        self.relation = list()
        self.value_props = list()
        self.entity = result.get('entity')
        self.entity = [e for e in self.entity if e['type'].lower() != "date"]
        if len(self.entity) > 1:
            self.scope_correction()
            self.entity_check()
        self.entity.extend(result.get('accounts'))
        self.relation = result.get('relation')
        self.value_props = vp_matcher.match(sentence)
        self.scope_correction()
        self.relation_filter()

        # 判断一个mention是实体还是关系
        self.relation_or_entity()
        self.set_mentions(self.entity, 'entity')
        self.set_mentions(self.relation, 'relation')
        self.set_mentions(self.value_props, 'value_props')

        if len(result.get("entity") + result.get("accounts")) == 0:
            logger.error(sentence + "\t实体识别模块返回空值")

    def relation_or_entity(self):
        """
        判断一个mention是实体还是关系
        若实体和关系end相同，删除关系，如汪鹏老师和老师
        若实体和关系end,begin相同，且实体类型为称谓，删除实体，如同学
        :return:
        """
        for e in self.entity:
            self.relation = [x for x in self.relation if x['end'] != e['end'] or x['begin'] == e['begin']]
        for r in self.relation:
            self.entity = [x for x in self.entity if x['end'] != r['end'] or x['begin'] != r['begin']
                           or x['type'] != 'chenwei']

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
        person_types = ['firstname', 'lastname', 'chenwei', 'person']
        addr_types = ["addr", "addr_value"]
        self.entity = sorted(self.entity, key=lambda x: x['begin'])
        new_entity = list()
        e1 = self.entity[0]
        for e2 in self.entity[1:]:
            if (e2['type'] in person_types and e1['type'] in person_types) or\
                    (e2['type'] in addr_types and e1['type'] in addr_types):
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
        new_account_dict = dict()
        for k, v in account_dict.items():
            new_account_dict[k.lower()] = v
        for e in self.entity:
            rel_list = new_account_dict.get(e['type'])
            if not rel_list:
                continue
            for rel_name in rel_list:
                new_relation = list()
                for r in self.relation:
                    if r['type'].lower() != rel_name.lower() \
                            or max(e['begin'], r['begin'])-min(e['end'], r['end']) > 4:
                        new_relation.append(r)
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
    person_types = ['firstname', 'lastname', 'chenwei', 'person']
    if e1['type'] in person_types:
        r_entity['type'] = 'person'
    else:
        r_entity['type'] = e1['type']
    r_entity['value'] = e1['value'] + e2['value']
    r_entity['code'] = e1['code']
    r_entity['begin'] = e1['begin']
    r_entity['end'] = e2['end']
    detail = e1.get('detail')
    if detail:
        detail.append(e2)
        r_entity['detail'] = detail
    else:
        r_entity['detail'] = [e1, e2]
    return r_entity


def main():
    """
    程序入口
    :return:
    """
    sentence = "东南大学汪鹏老师的学生张三"
    m_collector = MentionCollector(sentence)

    for m in m_collector.mentions:
        print(m)

    deps = dep_analyzer.get_result(sentence)
    for d in deps:
        print(d)


if __name__ == '__main__':
    main()
