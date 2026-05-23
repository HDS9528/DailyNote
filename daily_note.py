# -*- coding: utf8 -*-
import requests, json
from os import environ
from datetime import datetime
environ['NO_PROXY'] = '*'

# ====================== 配置区（只改这两个）======================
WEWORK_WEBHOOK = "https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=1e7a494e-2dc8-43f8-a917-ba123adb424d"
CITY_CODE = "101010100"  # 北京，换成你城市代码
# =================================================================

# ---------- 天气（不变）----------
def weather_info(city_code, timestamps):
    w_headers = {
        "User-Agent": "Mozilla/5.0",
        "Referer": "http://www.weather.com.cn/"
    }
    try:
        weather_url = f'http://d1.weather.com.cn/dingzhi/{city_code}.html?_={timestamps}'
        weather_req = requests.get(weather_url, headers=w_headers, timeout=10).text
        weather_info = json.loads(weather_req.replace(f"var cityDZ{city_code} =", "")
                                   .split(f";var alarmDZ{city_code} =")[0])['weatherinfo']
        warning_info = "当前无预警信息"
        return (
            f"城市名称：{weather_info['cityname']}\n"
            f"当前温度：{weather_info['temp']}\n"
            f"最低温度：{weather_info['tempn']}\n"
            f"天气情况：{weather_info['weather']}\n"
            f"风力风向：{weather_info['wd']}{weather_info['ws']}\n"
            f"预警信息：{warning_info}"
        )
    except:
        return "天气获取失败"

# ---------- 知乎热榜（替换原来的新浪新闻）----------
def get_news(*args):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Referer": "https://www.zhihu.com/hot"
    }
    url = "https://www.zhihu.com/api/v3/feed/topstory/hot-lists/total"
    params = {"limit": 50, "desktop": "true"}
    try:
        res = requests.get(url, headers=headers, params=params, timeout=10)
        data = res.json()
        items = data.get("data", [])
        news_list = []
        for item in items[:10]:  # 只取前10条
            target = item.get("target", {})
            title = target.get("title", "").strip()
            if title:
                news_list.append(title)
        return news_list if news_list else ["暂无知乎热榜"]
    except Exception as e:
        return [f"知乎热榜获取失败：{str(e)}"]

# ---------- 每日一句（不变）----------
def get_sentence():
    try:
        res = requests.get("https://v1.hitokoto.cn?c=d&c=h&c=i&c=k").json()
        return f"{res['hitokoto']}\n出自：{res['from']}"
    except:
        return "每天进步一点点"

# ---------- 组装消息（不变）----------
def message_content(city_code, timestamps, info_time, news_list, sentence):
    week_dict = {0:"星期一",1:"星期二",2:"星期三",3:"星期四",4:"星期五",5:"星期六",6:"星期日"}
    day = datetime.strftime(info_time, "%Y-%m-%d") + " " + week_dict[datetime.weekday(info_time)]
    content = (
        f"******{day}******\n"
        "*************天气************\n\n"
        f"{weather_info(city_code, timestamps)}\n\n"
        "*************知乎热榜************\n\n"
        + "\n".join(news_list) + "\n\n"
        "*************一句************\n\n"
        f"{sentence}"
    )
    return content

# ---------- 企业微信Webhook推送（不变）----------
def weixin_push(content):
    data = {
        "msgtype": "text",
        "text": {"content": content}
    }
    requests.post(WEWORK_WEBHOOK, json=data)

# ===================== 主程序 =====================
if __name__ == '__main__':
    info_time = datetime.now()
    timestamps = round(datetime.timestamp(info_time)*1000)
    content = message_content(
        CITY_CODE,
        timestamps,
        info_time,
        get_news(),
        get_sentence()
    )
    weixin_push(content)
    print("✅ 推送成功！")
