import hashlib
def  get_md5(url):
    #用md5的时候需要转码
    m = hashlib.md5()

    m.update(url.encode('utf-8'))
    return m.hexdigest()
