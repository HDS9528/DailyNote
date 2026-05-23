# -*- coding: utf8 -*-
import requests, json
from os import environ
from datetime import datetime
environ['NO_PROXY'] = '*'

# ====================== 你只需要改这里 1 个 ======================
WEWORK_WEBHOOK = "https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=1e7a494e-2dc8-43f8-a917-ba123adb424d"
CITY_CODE = "101010100"  # 北京  自己换城市代码
# =================================================================

def weather_info(city_code, timestamps):
    w_headers = {
        "User-Agent": "Mozilla/5.0",
        "Referer": "http://www.weather.com.cn/"
    }
    try:
        weather_url = f'http://d1.weather.com.cn/dingzhi/{city_code}.html?_={timestamps}'
        weather_req = requests.get(weather_url, headers=w_headers, timeout=10).text
        weather_info = json.loads(weather_req.replace(f"var cityDZ{city_code} =", "").split(f";var alarmDZ{city_code} =")[0])['weatherinfo']
        warning_info = "当前无预警信息"

        weather_messages = (
            "城市名称：%s" % weather_info['cityname'] +
            "\n当前温度：%s" % weather_info['temp'] +
            "\n最低温度：%s" % weather_info['tempn'] +
            "\n天气情况：%s" % weather_info['weather'] +
            "\n风力风向：%s" % weather_info['wd'] + weather_info['ws'] +
            "\n预警信息：%s" % warning_info
        )
        return weather_messages
    except:
        return "天气获取失败"

def get_news(news_type, news_time):
    news_headers = {
        "User-Agent": "Mozilla/5.0",
        "Referer": "http://news.sina.com.cn/"
    }
    try:
        news_url = f'http://top.news.sina.com.cn/ws/GetTopDataList.php?top_type=day&top_cat={news_type}&top_time={news_time}&top_show_num=20'
        news_req = requests.get(news_url, headers=news_headers).text.replace("var news_ = ","").replace(r"\/\/","//").replace(";","")
        news_sub = json.loads(news_req)['data']
        news_list = []
        for item in news_sub:
            if str(item['url']).startswith("https://video"):
                continue
            news_list.append(item['title'])
        return news_list
    except:
        return ["新闻获取失败"]

def get_sentence():
    try:
        res = requests.get("https://v1.hitokoto.cn?c=d&c=h&c=i&c=k").json()
        return f"{res['hitokoto']}\n出自：{res['from']}"
    except:
        return "每天进步一点点"

def message_content(city_code, timestamps, info_time, news_list, sentence):
    week_dict = {0:"星期一",1:"星期二",2:"星期三",3:"星期四",4:"星期五",5:"星期六",6:"星期日"}
    day = datetime.strftime(info_time, "%Y-%m-%d") + " " + week_dict[datetime.weekday(info_time)]
    content = (
        f"******{day}******\n"
        "*************天气************\n\n"
        f"{weather_info(city_code, timestamps)}\n\n"
        "*************热闻************\n\n"
        f"\n".join(news_list[:10]) + "\n\n"
        "*************一句************\n\n"
        f"{sentence}"
    )
    return content

# Webhook 推送（最简单！）
def weixin_push(content):
    data = {
        "msgtype": "text",
        "text": {
            "content": content
        }
    }
    requests.post(WEWORK_WEBHOOK, json=data)

# ===================== 主程序 =====================
if __name__ == '__main__':
    info_time = datetime.now()
    timestamps = round(datetime.timestamp(info_time)*1000)
    news_type = "news_china_suda"
    news_time = datetime.strftime(info_time,"%Y%m%d")

    content = message_content(
        CITY_CODE,
        timestamps,
        info_time,
        get_news(news_type, news_time),
        get_sentence()
    )
    weixin_push(content)
    print("✅ 推送成功！")
