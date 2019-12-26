# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html
from scrapy.loader import ItemLoader
import scrapy
from scrapy.loader.processors import MapCompose, TakeFirst, Join
import datetime
# from ..Spider.models.es_article_types import ArticType
from .models.es_article_types import ArticType
from .models.Technology_types import TechnologyType
from .models.Answer_type import AnswerType
from w3lib.html import remove_tags
from elasticsearch_dsl.connections import connections
import redis
import  re
from .utils.common import get_md5

redis_cli=redis.StrictRedis()
def gen_suggest(index, info_tuple):
    # 根据字符串生成搜索建议数组
    """Hell0STN
    此函数主要用于,连接elasticsearch(搜索引擎)，使用ik_max_word分词器，将传入的字符串进行分词，返回分词后的结果
    此函数需要两个参数：
    第一个参数：要调用elasticsearch(搜索引擎)分词的索引index，一般是（索引操作类._doc_type.index）
    第二个参数：是一个元组，元祖的元素也是元组，元素元祖里有两个值一个是要分词的字符串，第二个是分词的权重，多个分词传多个元祖如下
    书写格式：
    gen_suggest(lagouType._doc_type.index, (('字符串', 10),('字符串', 8)))
    """# 连接elasticsearch(搜索引擎)，使用操作搜索引擎的类下面的_doc_type.using连接
    es = connections.create_connection(TechnologyType._doc_type.using)
    used_words = set()
    suggests = []
    for text, weight in info_tuple:
        if text:
            # 调用es的analyze接口分析字符串，
            words = es.indices.analyze(index=index, analyzer="ik_max_word", params={'filter':["lowercase"]}, body=text)
            anylyzed_words = set([r["token"] for r in words["tokens"] if len(r["token"])>1])
            new_words = anylyzed_words - used_words
        else:
            new_words = set()
        if new_words:
            suggests.append({"input":list(new_words), "weight":weight})
    return suggests

def item_create_date(value):
    try:
        create_data = datetime.datetime.strptime(value, "%Y/%m/%d").date()
    except Exception as e:
        create_data = datetime.datetime.now().date()
    return create_data


def get_praise_num(value):
    if len(value[0].strip()) == 0 or value is None:
        value = 0
    else:
        value = value
    return value


def get_num(value):
    strip_1 = value.strip()
    split_2 = strip_1.split(" ")
    split_3 = split_2[0]
    if not split_3.isdigit():
        return "0"
    print(split_3)
    return split_3


def remove_comment(value):
    if '评论' in value:
        return ''
    else:
        return value
def get_int_num(value):
    if re.match('.*?(\d+).*', value):
        num = int(re.match('.*?(\d+).*', value).group(1))
    else:
        num = 0
    return num


def change_num(value):
    if ',' in value:
        return ''.join(value.split(','))
    else:
        return value


# class QuestionLoader(ItemLoader):
#     default_output_processor = TakeFirst()


# class AnswerLoader(ItemLoader):
#     default_output_processor = TakeFirst()
def change_time(value):
    if "发布于" in value:
        return  "".join(value.replace("发布于 ",''))
    else:
        return  value
def md5(value):
    print(value)
    return  get_md5(value)

class  csdnitem(scrapy.Item):
    title = scrapy.Field()
    link_url = scrapy.Field()
    content = scrapy.Field()
    source = scrapy.Field()
    time = scrapy.Field()
    url_object_id = scrapy.Field()
    read_num=scrapy.Field()
    comment_num=scrapy.Field()
    tag=scrapy.Field()
    def  save_artic_to_es(self):
        Tec_article=TechnologyType()
        Tec_article.time=self['time']
        Tec_article.read_num=self['read_num']
        Tec_article.content=remove_tags(self["content"])
        Tec_article.link_url=self['link_url']
        Tec_article.title=self['title']
        Tec_article.comment_num=self['comment_num']
        Tec_article.source=self['source']
        Tec_article.meta.id =self['url_object_id']
        Tec_article.tag=self['tag']
        Tec_article.suggest = gen_suggest(Tec_article._doc_type.index, ((Tec_article.title, 10),(Tec_article.tag,7)))
        Tec_article.save()
        redis_cli.incr("CSDN")
        return

class  BokeYuanItem(scrapy.Item):
    title = scrapy.Field()
    link_url = scrapy.Field()
    content = scrapy.Field()
    source = scrapy.Field()
    time = scrapy.Field()
    comment_num=scrapy.Field()#评论数
    read_num=scrapy.Field()#阅读数
    url_object_id = scrapy.Field()
    def save_artic_to_es(self):
        Tec_article = TechnologyType()
        Tec_article.title = self['title']
        Tec_article.link_url = self['link_url']
        Tec_article.content = remove_tags(self['content'])
        Tec_article.source = self['source']
        Tec_article.time = self['time']
        Tec_article.comment_num = self['comment_num'] # 评论数
        Tec_article.read_num = self['read_num'] # 阅读数
        Tec_article.meta.id = self['url_object_id']

        Tec_article.suggest = gen_suggest(Tec_article._doc_type.index, ((Tec_article.title, 10)))
        Tec_article.save()
        redis_cli.incr("BokeYuan")
        return
class five_one_ctoItem(scrapy.Item):
    title = scrapy.Field()
    link_url = scrapy.Field()
    content = scrapy.Field()
    source = scrapy.Field()
    time=scrapy.Field()
    Collection_num=scrapy.Field()#收藏数
    read_num = scrapy.Field()
    comment_num = scrapy.Field()
    url_object_id = scrapy.Field()
    tag=scrapy.Field()
    def save_artic_to_es(self):
        Tec_article = TechnologyType()
        Tec_article.title = self['title']
        Tec_article.link_url =self['link_url']
        Tec_article.content = self['content']
        Tec_article.source = self['source']
        Tec_article.time = self['time']
        Tec_article. Collection_num = self['Collection_num']  # 收藏数
        Tec_article.read_num = self['read_num']
        Tec_article.comment_num = self['comment_num']
        Tec_article.meta.id = self['url_object_id']
        Tec_article.tag=self['tag']
        Tec_article.suggest = gen_suggest(Tec_article._doc_type.index, ((Tec_article.title, 10),(Tec_article.tag, 7)))
        Tec_article.save()
        redis_cli.incr("51cto")
        return
class  itpubItem(scrapy.Item):
    title=scrapy.Field()
    link_url = scrapy.Field()
    time=scrapy.Field()
    tag=scrapy.Field()
    comment_num=scrapy.Field()
    content=scrapy.Field()
    source=scrapy.Field()
    url_object_id = scrapy.Field()
    def save_artic_to_es(self):
        Tec_article = TechnologyType()
        Tec_article.title =self['title']
        Tec_article.link_url = self['link_url']
        Tec_article.time = self['time']
        Tec_article.tag = self['tag']
        Tec_article.comment_num = self['comment_num']
        Tec_article.content = remove_tags(self['content'])
        Tec_article.source = self['source']
        Tec_article.meta.id = self['url_object_id']

        Tec_article.suggest = gen_suggest(Tec_article._doc_type.index, ((Tec_article.title, 10), (Tec_article.tag, 7)))
        Tec_article.save()
        redis_cli.incr("itpub")
        return
class  oschina(scrapy.Item):
    title=scrapy.Field()
    time=scrapy.Field()
    content=scrapy.Field()
    link_url = scrapy.Field()
    url_object_id = scrapy.Field()
    source=scrapy.Field()
    comment_num = scrapy.Field()
    Collection_num = scrapy.Field()  # 收藏数
    read_num = scrapy.Field()
    praise_num = scrapy.Field()
    tag=scrapy.Field()
    def save_artic_to_es(self):
        Tec_article = TechnologyType()
        Tec_article.title = self['title']
        Tec_article.time = self['time']
        Tec_article.content =remove_tags(self['content'])
        Tec_article.link_url = self['link_url']
        Tec_article.meta.id = self['url_object_id']
        Tec_article.source = self['source']
        Tec_article.comment_num = self['comment_num']
        Tec_article. Collection_num = self['Collection_num'] # 收藏数
        Tec_article.read_num = self['read_num']
        Tec_article.praise_num = self['praise_num']
        Tec_article.tag = self['tag']
        Tec_article.suggest = gen_suggest(Tec_article._doc_type.index, ((Tec_article.title, 10), (Tec_article.tag, 7)))
        Tec_article.save()
        redis_cli.incr("OSCHINA")
        return
class  Segmentfault(scrapy.Item):
    title = scrapy.Field()
    time = scrapy.Field()
    content = scrapy.Field()
    link_url = scrapy.Field()
    url_object_id = scrapy.Field()
    source = scrapy.Field()
    tag = scrapy.Field()
    read_num = scrapy.Field()
    def save_artic_to_es(self):
        Tec_article = TechnologyType()
        Tec_article.title = self['title']
        Tec_article.time = self['time']
        Tec_article.content = remove_tags(self['content'])
        Tec_article.link_url = self['link_url']
        Tec_article.meta.id = self['url_object_id']
        Tec_article.source = self['source']
        Tec_article.tag = self['tag']
        Tec_article.read_num = self['read_num']
        Tec_article.suggest = gen_suggest(Tec_article._doc_type.index, ((Tec_article.title, 10), (Tec_article.tag, 7)))
        Tec_article.save()
        redis_cli.incr("Segmentfault")
        return

class QuestionLoader(ItemLoader):
    default_output_processor = TakeFirst()
class QuestionItem(scrapy.Item):
        zhihu_id = scrapy.Field()
        topic = scrapy.Field(output_processor=Join(','))
        link_url = scrapy.Field(input_processor=MapCompose(md5))
        title = scrapy.Field()
        content = scrapy.Field()
        answer_num = scrapy.Field(input_processor=MapCompose(change_num, get_int_num))#回答数
        comment_num = scrapy.Field(input_processor=MapCompose(change_num, get_int_num))#评论数
        #关注着数量
        watcher_num = scrapy.Field(input_processor=MapCompose(change_num, get_int_num))
        # 点击数
        click_num = scrapy.Field(input_processor=MapCompose(change_num, get_int_num))
        time=scrapy.Field()
        source=scrapy.Field()
        def save_artic_to_es(self):
            Tec_article = TechnologyType()
            Tec_article.title = self['title']
            Tec_article.time = self['time']
            Tec_article.content = remove_tags(self['content'])
            Tec_article.link_url = self['link_url']
            Tec_article.meta.id = self['zhihu_id']
            Tec_article.source = self['source']
            Tec_article.tag = self['topic']
            Tec_article.read_num = self['click_num']
            Tec_article.comment_num=self['comment_num']
            Tec_article.suggest = gen_suggest(Tec_article._doc_type.index,((Tec_article.title, 10), (Tec_article.tag, 7)))
            Tec_article.save()
            redis_cli.incr("zhihu")
            return
class  lagouItem(scrapy.Item):
     jobname=scrapy.Field()
     publish_time=scrapy.Field()
     max_salary=scrapy.Field()
     min_salary=scrapy.Field()
     workaddr=scrapy.Field()
     tags=scrapy.Field()
     work_duty=scrapy.Field()
     work_ask=scrapy.Field()
     work_time=scrapy.Field()
     work_exp=scrapy.Field()#工作经验
     education=scrapy.Field()#学历
     company_name=scrapy.Field()
     company_field=scrapy.Field()
     company_size=scrapy.Field()
     company_url=scrapy.Field()

class yixieshiItem(scrapy.Item):
     title=scrapy.Field()
     link_url=scrapy.Field()
     time=scrapy.Field()
     content=scrapy.Field()
     tags=scrapy.Field()
     source=scrapy.Field()
     url_object_id = scrapy.Field()

     def save_artic_to_es(self):
         Tec_article = TechnologyType()
         Tec_article.title = self['title']
         Tec_article.time = self['time']
         Tec_article.content = remove_tags(self['content'])
         Tec_article.link_url = self['link_url']
         Tec_article.meta.id = self['url_object_id']
         Tec_article.source = self['source']
         Tec_article.tag = self['tags']
         Tec_article.suggest = gen_suggest(Tec_article._doc_type.index, ((Tec_article.title, 10), (Tec_article.tag, 7)))
         Tec_article.save()
         redis_cli.incr("yixieshi")
         return
class Aliyun_tec(scrapy.Field):
    title=scrapy.Field()
    tags=scrapy.Field()
    time=scrapy.Field()
    content=scrapy.Field()
    link_url=scrapy.Field()
    url_object_id = scrapy.Field()
    source = scrapy.Field()

    def save_artic_to_es(self):
        Tec_article = TechnologyType()
        Tec_article.title = self['title']
        Tec_article.time = self['time']
        Tec_article.content = remove_tags(self['content'])
        Tec_article.link_url = self['link_url']
        Tec_article.meta.id = self['url_object_id']
        Tec_article.source = self['source']
        Tec_article.tag = self['tags']
        Tec_article.suggest = gen_suggest(Tec_article._doc_type.index, ((Tec_article.title, 10), (Tec_article.tag, 7)))
        Tec_article.save()
        redis_cli.incr("aliyun")
        return
class  iteye(scrapy.Field):
    title = scrapy.Field()
    tags = scrapy.Field()
    time = scrapy.Field()
    content = scrapy.Field()
    link_url = scrapy.Field()
    url_object_id = scrapy.Field()
    source = scrapy.Field()

    def save_artic_to_es(self):
        Tec_article = AnswerType()
        Tec_article.title = self['title']
        Tec_article.time = self['time']
        Tec_article.content = remove_tags(self['content'])
        Tec_article.link_url = self['link_url']
        Tec_article.meta.id = self['url_object_id']
        Tec_article.source = self['source']
        Tec_article.tag = self['tags']
        Tec_article.suggest = gen_suggest(Tec_article._doc_type.index, ((Tec_article.title, 10), (Tec_article.tag, 7)))
        Tec_article.save()
        redis_cli.incr("iteye")
        return

