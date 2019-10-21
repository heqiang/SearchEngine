# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
from  scrapy.pipelines.images import ImagesPipeline

class SearchEnginePipeline(object):
    def process_item(self, item, spider):
        return item

#返回图片保存的路径
class  ArticleImagePipeline(ImagesPipeline):
    def item_completed(self, results, item, info):
        for ok ,value  in results:
            if value["path"]:
                front_image_path=value['path']
            else:
                front_image_path=None
        item['front_image_path']=front_image_path#路径填充
        return item
#将数据插入es数据库
class  ElasticsearchPipeline(object):

    def  process_item(self,item,spider):
        #将item转化为es的格式
        item.save_artic_to_es()
        return item