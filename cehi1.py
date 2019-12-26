import pandas as pd
from collections import Counter
import  re
from collections import Counter

# list_keyword=['Elasticsearch', 'elasticsearch', '入门', '交互', '基础', 'Elasticsearch', 'elasticsearch', '入门', '交互', '基础', 'python', 'scrapy', 'Elasticsearch', 'elasticsearch', '入门', '交互', '基础', 'python', 'scrapy', 'python', 'scrapy', 'python', 'scrapy', 'java', 'spring', 'Elasticsearch', 'elasticsearch', '入门', '交互', '基础', 'Elasticsearch', 'elasticsearch', '入门', '交互', '基础', 'Elasticsearch', 'elasticsearch', '入门', '交互', '基础', 'Elasticsearch', 'elasticsearch', '入门', '交互', '基础', 'Elasticsearch', 'elasticsearch', '入门', '交互', '基础', 'Elasticsearch', 'elasticsearch', '入门', '交互', '基础', 'java', '速成', 'java', 'spring', 'java', 'spring', '多线程', 'Java', '进阶', 'atomic', 'AtomicReference', '框架', '十四']
# result=pd.value_counts(list_keyword)
# result2=Counter(list_keyword)
import  threading


def  add():
    return 5

if __name__ == '__main__':
    res = threading.Thread(target=add)
    res.start()
    result=res.join()
    print(result.get_result())




