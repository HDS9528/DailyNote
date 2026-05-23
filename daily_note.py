# -*- coding: utf8 -*-
import requests
from datetime import datetime

# ====================== 你只需要填这里 ======================
WEWORK_WEBHOOK = "https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=1e7a494e-2dc8-43f8-a917-ba123adb424d"
CITY_CODE = "101230704"  # 福建省 龙岩市 武平县
# ============================================================

def weather_info(city_code):
    try:
        url = f"http://d1.weather.com.cn/dingzhi/{city_code}.html"
        headers = {
            "User-Agent": "Mozilla/5.0",
            "Referer": "http://www.weather.com.cn/"
        }
        res = requests.get(url, headers=headers, timeout=10)
        res.encoding = "utf-8"
        data = res.text.split(f"var cityDZ{city_code} =")[1].split(";var alarmDZ")[0]
        import json
        weather = json.loads(data)["weatherinfo"]
        return (
            f"城市：{weather['cityname']}\n"
            f"温度：{weather['temp']}\n"
            f"最低：{weather['tempn']}\n"
            f"天气：{weather['weather']}\n"
            f"风力：{weather['wd']}{weather['ws']}"
        )
    except Exception as e:
        return f"天气获取失败"

# 你指定的 60s 接口！
def get_60s_news():
    try:
        url = "https://60s.gsyy.eu.org/v2/60s?encoding=text"
        res = requests.get(url, timeout=10)
        res.encoding = "utf-8"
        lines = res.text.strip().splitlines()
        return [line.strip() for line in lines if line.strip()]
    except:
        return ["新闻获取失败"]

def get_sentence():
    try:
        res = requests.get("https://v1.hitokoto.cn", timeout=5).json()
        return f"{res['hitokoto']}\n出自：{res['from']}"
    except:
        return "保持热爱，奔赴山海"

def build_msg():
    now = datetime.now()
    week = ["星期一","星期二","星期三","星期四","星期五","星期六","星期日"][now.weekday()]
    date = now.strftime("%Y-%m-%d")

    weather = weather_info(CITY_CODE)
    news = get_60s_news()
    sentence = get_sentence()

    msg = f"""
****** {date} {week} ******

============= 天气 =============
{weather}

============= 60秒读懂世界 =============
"""
    for line in news:
        msg += line + "\n"

    msg += f"""
============= 每日一句 =============
{sentence}
"""
    return msg

def push(content):
    data = {
        "msgtype": "text",
        "text": {"content": content}
    }
    requests.post(WEWORK_WEBHOOK, json=data)
    print("✅ 推送成功！")

if __name__ == "__main__":
    msg = build_msg()
    print(msg)
    push(msg)
