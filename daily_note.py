# -*- coding: utf8 -*-
import requests
from datetime import datetime
import json

# ==================== 【中心化配置模块】 ====================
CONFIG = {
    "WEBHOOK_URL": "https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=1e7a494e-2dc8-43f8-a917-ba123adb424d",
    "CITY_LIST": [
        ("武平", "101230704"),
        ("龙泉", "101210803")
    ],
    "API_BASE": "https://60s.viki.moe",
    "TIMEOUT": 10
}

# 接口地址统一在这里加
API = {
    "fuel": f"{CONFIG['API_BASE']}/v2/fuel-price?region=浙江&encoding=text",
    "moyu": f"{CONFIG['API_BASE']}/v2/moyu?encoding=text"
}

# ==================== 【天气获取模块】 ====================
def get_current_weather(city_name, city_code):
    try:
        url = f"http://d1.weather.com.cn/dingzhi/{city_code}.html"
        headers = {
            "User-Agent": "Mozilla/5.0",
            "Referer": "http://www.weather.com.cn/"
        }
        res = requests.get(url, headers=headers, timeout=CONFIG["TIMEOUT"])
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

# ==================== 【各类信息获取模块】 ====================
def get_fuel_price():
    try:
        res = requests.get(API["fuel"], timeout=CONFIG["TIMEOUT"])
        res.encoding = "utf-8"
        return res.text.strip()
    except:
        return "油价信息获取失败"

def get_moyu():
    try:
        res = requests.get(API["moyu"], timeout=CONFIG["TIMEOUT"])
        res.encoding = "utf-8"
        return res.text.strip()
    except:
        return "摸鱼日报获取失败"

# ==================== 【消息组装模块】 ====================
def build_message():
    now = datetime.now()
    week_arr = ["星期一", "星期二", "星期三", "星期四", "星期五", "星期六", "星期日"]
    date_str = now.strftime("%Y-%m-%d")
    week_str = week_arr[now.weekday()]

    weather_content = ""
    for name, code in CONFIG["CITY_LIST"]:
        weather_content += get_current_weather(name, code) + "\n\n"

    fuel = get_fuel_price()
    moyu = get_moyu()

    msg = f"""
****** {date_str} {week_str} ******

============= 天气预报 =============
{weather_content}
============= 今日油价 =============
{fuel}

============= 摸鱼日报 =============
{moyu}
"""
    return msg

# ==================== 【推送模块】 ====================
def send_message(content):
    payload = {
        "msgtype": "text",
        "text": {"content": content}
    }
    requests.post(CONFIG["WEBHOOK_URL"], json=payload)
    print("✅ 推送成功")

# ==================== 【主入口】 ====================
if __name__ == "__main__":
    final_msg = build_message()
    print(final_msg)
    send_message(final_msg)
