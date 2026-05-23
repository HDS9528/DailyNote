# -*- coding: utf8 -*-
import requests
from datetime import datetime
import json

# ========== 中心化全局配置 ==========
WEBHOOK_URL = "https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=f1d36ecd-288b-4531-a7fd-47da8db862ec"
CITY_LIST = [
    ("武平", "101230704"),
    ("龙泉", "101210803")
]
API_BASE = "https://60s.gsyy.eu.org"
NEWS_API = f"{API_BASE}/v2/60s?encoding=text"
FUEL_API = f"{API_BASE}/v2/fuel-price?encoding=text"
# 通用请求头
COMMON_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
}
# ==================================

def get_single_weather(city_name, city_code):
    try:
        url = f"http://d1.weather.com.cn/dingzhi/{city_code}.html"
        headers = {
            "User-Agent": "Mozilla/5.0",
            "Referer": "http://www.weather.com.cn/"
        }
        res = requests.get(url, headers=headers, timeout=10)
        res.encoding = "utf-8"
        data = res.text.split(f"var cityDZ{city_code} =")[1].split(";var alarmDZ")[0]
        weather = json.loads(data)["weatherinfo"]
        return (
            f"【{city_name}】\n"
            f"温度：{weather['temp']}\n"
            f"最低：{weather['tempn']}\n"
            f"天气：{weather['weather']}\n"
            f"风力：{weather['wd']}{weather['ws']}"
        )
    except:
        return f"【{city_name}】天气获取失败"

def get_news():
    try:
        res = requests.get(NEWS_API, headers=COMMON_HEADERS, timeout=10)
        res.encoding = "utf-8"
        return [line.strip() for line in res.text.strip().splitlines() if line.strip()]
    except:
        return ["新闻获取失败"]

def get_fuel_price():
    try:
        res = requests.get(FUEL_API, headers=COMMON_HEADERS, timeout=10)
        res.encoding = "utf-8"
        return res.text.strip()
    except:
        return "油价信息获取失败"

def get_hitokoto():
    try:
        res = requests.get("https://v1.hitokoto.cn", timeout=5).json()
        return f"{res['hitokoto']}\n出自：{res['from']}"
    except:
        return "保持热爱，奔赴山海"

def build_message():
    now = datetime.now()
    week_arr = ["星期一","星期二","星期三","星期四","星期五","星期六","星期日"]
    date_str = now.strftime("%Y-%m-%d")
    week_str = week_arr[now.weekday()]

    weather_content = ""
    for name, code in CITY_LIST:
        weather_content += get_single_weather(name, code) + "\n\n"

    news_content = get_news()
    fuel_content = get_fuel_price()
    sentence = get_hitokoto()

    msg = f"""
****** {date_str} {week_str} ******

============= 天气预报 =============
{weather_content}
============= 今日油价 =============
{fuel_content}

============= 60秒读懂世界 =============
"""
    for item in news_content:
        msg += item + "\n"

    msg += f"""
============= 每日一句 =============
{sentence}
"""
    return msg

def send_push(content):
    payload = {
        "msgtype": "text",
        "text": {"content": content}
    }
    requests.post(WEBHOOK_URL, json=payload)
    print("✅ 推送成功")

if __name__ == "__main__":
    final_msg = build_message()
    print(final_msg)
    send_push(final_msg)
