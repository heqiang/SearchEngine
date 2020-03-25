from  datetime import datetime
from elasticsearch_dsl import DocType,Date,Nested,Boolean,\
    analyzer,Completion,Text,Keyword,Integer,tokenizer
from elasticsearch_dsl.connections import connections

from elasticsearch_dsl.analysis import CustomAnalyzer as _CustomAnalyzer

connections.create_connection(hosts=["localhost"])
#类重写
class CustomAnalyzer(_CustomAnalyzer):                                      # 自定义CustomAnalyzer类，来重写CustomAnalyzer类

    def get_analysis_definition(self):
        return {}
ik_analyzer = CustomAnalyzer("ik_max_word", filter=["lowercase"])
class  AnswerType(DocType):
     suggest=Completion(analyzer=ik_analyzer)
     title=Text(analyzer='ik_max_word')
     time=Date()
     link_url=Keyword()
     content=Text(analyzer='ik_max_word')
     url_object_id = Keyword()
     tag=Text(analyzer='ik_max_word')#标签
     comment_num = Integer()#评论数
     read_num = Integer()#阅读数
     Collection_num = Integer()#收藏数
     praise_num=Integer()#点赞数
     source=Keyword()#来源
     class Meta:
         index="answer" #必须小写
         doc_type="tec_answer"
if __name__ == '__main__':
    AnswerType.init()


