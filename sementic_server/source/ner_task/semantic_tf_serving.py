"""
@description: 命名实体识别模块
@author: Cui Rui long
@email: xiaocuikindle@163.com
@time: 2019-02-27
@version: 0.0.1
"""
import jieba
import logging

from sementic_server.source.ner_task.entity_code import EntityCode
from sementic_server.source.ner_task.system_info import SystemInfo
from sementic_server.source.ner_task.model_tf_serving import ModelServing
from sementic_server.source.ner_task.account import Account

logger = logging.getLogger("server_log")


class SemanticSearch(object):
    """
    通过调用 sentence_ner_entities 函数实现对：人名、组织结构名、地名和日期 的识别
    """

    def __init__(self):

        self.system_info = SystemInfo()

        self.client = ModelServing(self.system_info.MODE_NER)
        self.account = Account()
        self.config = self.system_info.get_config()
        self.entity_code = EntityCode()
        self.ner_entities = self.entity_code.get_ner_entities()
        self.code = self.entity_code.get_entity_code()
        self.entity_map_dic = {"ORG": "cpny_name", "FNAME": "firstname", "LNAME": "lastname", "CW": "chenwei",
                               "DATE": "date", "LOC": "addr_value"}
        self.labels_list = []
        self.labels_list_split = []
        self.__init_specific_label_combine()
        self.__init_jieba()

    def __init_specific_label_combine(self):
        """
        初始化labels_list和labels_list_split列表
        用于将出现的此类标签：“NAMECOMPANY” 分开成 “NAME#COMPANY”
        :return:
        """
        entities = self.entity_code.get_entities()
        for i in range(0, len(entities)):
            for j in range(0, len(entities)):
                if i != j:
                    self.labels_list.append(entities[i] + entities[j])
                    self.labels_list_split.append((entities[i] + "#" + entities[j]))

                    self.labels_list.append(entities[j] + entities[i])
                    self.labels_list_split.append((entities[j] + "#" + entities[i]))

    def __init_jieba(self):
        """
        可以给分词工具加入领域词汇辅助分词，加入公司名称可以有效提升分词工具对公司名称分词的准确度
        :return:
        """
        entities = self.entity_code.get_entities()
        for label in entities:
            jieba.add_word(label)

    @staticmethod
    def __combine_label(entities, label=None):
        """
        合并实体列表中相连且相同的label
        :param entities:
        :param label:
        :return:
        """
        pre_label = False
        first_label = None
        entities_copy = []
        for i in range(len(entities)):
            if entities[i][1] != label:
                pre_label = False
                if first_label is not None:
                    entities_copy.append(first_label)
                    first_label = None
                entities_copy.append(entities[i])
            elif pre_label is False and entities[i][1] == label:
                pre_label = True
                first_label = entities[i]
            elif pre_label and first_label is not None and entities[i][1] == label:
                temp = first_label
                first_label = [temp[0] + entities[i][0], temp[1]]

        if first_label is not None:
            entities_copy.append(first_label)

        return entities_copy

    def __combine_com_add(self, entities):
        """
        合并 COMPANYADDR 和 ADDRCOMPANY 这类实体为 COMPANY
        :param entities:
        :return:
        """
        company_index = -1
        addr_index = -1

        for i, entity in enumerate(entities):
            if self.ner_entities['COMPANY'] == entity[1]:
                company_index = i
            if self.ner_entities['ADDR'] == entity[1]:
                addr_index = i
        if company_index != -1 and addr_index != -1:
            if company_index == addr_index + 1:
                entities[company_index][0] = entities[addr_index][0] + entities[company_index][0]
                entities.remove(entities[addr_index])
            elif company_index == addr_index - 1:
                entities[company_index][0] = entities[company_index][0] + entities[addr_index][0]
                entities.remove(entities[addr_index])

    def __split_diff_labels(self, template_sen):
        """
        检测模板句中是否有不同的label相互连接的情况，eg. "ADDRNAME"，这种情况分词工具无法正确分词
        如果存在相连的label，使用“#”将两个label分开
        :param template_sen: 模板句子
        :return:
        """
        for i, label in enumerate(self.labels_list):
            if label in template_sen:
                template_sen = template_sen.replace(label, self.labels_list_split[i])
        return template_sen

    @staticmethod
    def deal_B(self, word, pre_label, label, label1, temp_label, sentence, i, entities):
        """
        处理B开头的标签
        :param word:
        :param pre_label:
        :param label:
        :param label1:
        :param temp_label:
        :param sentence:
        :param i:
        :param entities:
        :return:
        """
        if word != "":
            if "##" in word:
                word = word.replace('##', '')
            if pre_label is not label:
                entities.append([word, label1])
            pre_label = label
            word = ""
        label1 = self.entity_map_dic[temp_label[2:]]
        label = temp_label[2:]
        word += sentence[i]
        return pre_label, label, label1, entities, word

    @staticmethod
    def deal_O(self, word, pre_label, entities, label1, label):
        """
        处理O开头的标签
        :param word:
        :param pre_label:
        :param entities:
        :param label1:
        :param label:
        :return:
        """
        if "##" in word:
            word = word.replace('##', '')
        if pre_label is not label:
            entities.append([word, label1])
        return entities

    @staticmethod
    def deal_BIO(self, sentence, pred_label_result,word,label,label1):
        """
        处理BIO开头的标签信息
        :param sentence:
        :param pred_label_result:
        :param entities:
        :return:
        """
        entities = []
        pre_label = pred_label_result[0]
        for i in range(len(sentence)):
            temp_label = pred_label_result[i]
            if temp_label[0] == 'B':
                pre_label, label, label1, entities, word = self.deal_B(self, word, pre_label, label, label1, temp_label,
                                                                       sentence, i, entities)
            elif temp_label[0] == 'I' and word != "":
                word += sentence[i]
            elif temp_label == 'O' and word != "":
                entities = self.deal_O(self, word, pre_label, entities, label1, label)
                pre_label = label
                word = ""
                label = ""
        return entities, label, label1, pre_label, word

    def __get_entities(self, sentence, pred_label_result):
        """
        根据BIO标签从识别结果中找出所有的实体
        :param sentence: 待识别的句子
        :param pred_label_result: 对该句子预测的标签
        :return: 返回识别的实体
        """
        word = ""
        label = ""
        label1= ""
        pre_label = pred_label_result[0]
        entities, label, label1, pre_label, word = self.deal_BIO(self, sentence, pred_label_result,word,label,label1)
        if word != "":
            if "##" in word:
                word = word.replace('##', '')
            if pre_label is not label:
                entities.append([word, label1])
        print(entities)
        return entities

    @staticmethod
    def pop_account(self, query, begin, end):
        """
        去除账号实体
        :param self:
        :param query:
        :param begin:
        :param end:
        :return:
        """
        account_result = self.account.get_account_labels_info(query)
        accounts = account_result['accounts']
        flag = 0
        for account in accounts:
            account_begin = account['begin']
            account_end = account['end']
            if begin >= account_begin and end <= account_end:
                flag = 1
                break
        return flag

    @staticmethod
    def pop_negative(word, label, neagtive_rel):
        """
        去除负样本实体
        :param word:
        :param label:
        :param neagtive_rel:
        :return:
        """
        flag = 0
        if '[UNK]' in word:
            flag = 1
        if word == 'im' and label == 'firstname':
            flag = 1
        if word == 'si' and label == 'lastname':
            flag = 1
        if word == '群' and label == 'firstname':
            flag = 1
        if label == 'chenwei' and word in neagtive_rel:
            flag = 1
        return flag

    @staticmethod
    def deal_label(label, word):
        if label == 'firstname' and len(word) > 2:
            label = 'cpny_name'
        return label
    
    @staticmethod
    def deal_addr(self, label, query):
        sentence, pred_label_result = self.client.send_grpc_request_ner(query.lower())
        entities = self.__get_entities(sentence, pred_label_result)
        for word, l in entities:
            if word == query.lower() and l == 'addr_value':
                label = l
        return label
    
    @staticmethod
    def entity_result(self, entities, query, neagtive_rel):
        """
        处理实体识别结果，去除账号和负样本等信息
        :param self:
        :param entities:
        :param query:
        :param neagtive_rel:
        :return:
        """
        entity = []
        prefix_len = 0
        end = 0
        for word, label in entities:
            sen = query.lower()[end:]
            begin = sen.find(word) + prefix_len
            end = begin + len(word)
            prefix_len = end
            if begin != -1 and word.isdigit() is False:
                neagtive_flag = self.pop_negative(word, label, neagtive_rel)
                label = self.deal_label(label, word)
                flag = self.pop_account(self, query, begin, end)
                if label == 'cpny_name':
                    w = query[begin:end]
                    label = self.deal_addr(self, label, w)
                if flag != 1 and neagtive_flag != 1:
                    entity.append({"type": label, "value": query[begin:end], "code": self.code[label], "begin": begin,
                                   "end": end})
        return entity

    def get_ner_result(self, query):
        """
        发送 gRPC 请求到 Docker 服务，对 query 进行命名实体识别
        :param query: 问句
        :return:
        """
        neagtive_rel = ['同伙', '同案', '同学', '初中同学', '小学同学', '高中同学', '大学同学', '中学同学', '中学', '博士生', '研究生', '大学', '老乡',
                        '幼儿园同学', '研究生同学', '博士生同学', '管理员', '管理', '员工', '同案人员', '同事', '大学导师', '同监人', '职员']
        sentence, pred_label_result = self.client.send_grpc_request_ner(query.lower())
        if pred_label_result is None:
            logger.error("句子: {0}\t实体识别结果为空".format(query))
            return None
        entities = self.__get_entities(sentence, pred_label_result)
        if len(entities) != 0:
            self.__combine_com_add(entities)
        entity = self.entity_result(self, entities, query, neagtive_rel)
        return entity, entities

    def sentence_ner_entities(self, result_intent):
        """
        使用 BERT 模型对句子进行实体识别，返回标记实体的句子
        :param result_intent: 意图识别模块的输出
        :return:
            entities: 列表，存储的是 BERT 识别出来的实体信息:(word, label)
            result: account_label 模块返回的结果
        """
        sentence = result_intent["query"]

        entity, entities = self.get_ner_result(sentence)
        logger.info(entity)
        result_intent["entity"] = entity

        # 如果识别的实体已经被识别为账户，那么其为账户的可能性更大，从实体列表里面去除该实体
        for index, entity in enumerate(result_intent["entity"]):
            for account in result_intent["accounts"]:
                if account["value"].find(entity["value"]) != -1:
                    temp = result_intent["entity"].pop(index)
                    print(temp)

        # 提取出账户识别模块识别的所有 UNLABEL 标签
        unlabels = []
        for value in result_intent["accounts"]:
            if value["type"] == "UNLABEL":
                unlabels.append(value["value"])
        if len(unlabels) == 0:
            unlabel_result = None
        else:
            unlabel_result = {"sentence": sentence, "unlabels": unlabels, "error": "账户类型不明确"}
        return result_intent, unlabel_result
