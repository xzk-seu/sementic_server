from sementic_server.source.intent_extraction.item_matcher import ItemMatcher
from sementic_server.source.ner_task.account import Account
from sementic_server.source.ner_task.semantic_tf_serving import SemanticSearch
from sementic_server.source.tool.v_prop_matcher import VpMatcher
from sementic_server.source.dep_analyze.get_analyze_result import DepAnalyzer

# NER & 匹配器
semantic = SemanticSearch()
item_matcher = ItemMatcher(True)
account = Account()
vp_matcher = VpMatcher()
dep_analyzer = DepAnalyzer()

