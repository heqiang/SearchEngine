from fake_useragent import UserAgent

def get_User_agent():
    ua=UserAgent()
    return  ua.random

