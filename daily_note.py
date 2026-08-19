# -*- coding: utf8 -*-
import requests
from datetime import datetime
import json
#https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=1e7a494e-2dc8-43f8-a917-ba123adb424d
# ==================== 【中心化配置模块】 ====================
CONFIG = {
    "WEBHOOK_URL": "https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=33a8f34a-6abe-434a-81ef-bb9a252cc3f1",
    # (显示名称 , query查询城市名)
    "CITY_LIST": [
        ("武平", "武平"),
        ("宁波-镇海", "镇海")
    ],
    "API_BASE": "https://60s.gsyy.help",
    "TIMEOUT": 10
}

API = {
    "fuel": f"{CONFIG['API_BASE']}/v2/fuel-price?region=浙江&encoding=text",
    "moyu": f"{CONFIG['API_BASE']}/v2/moyu?encoding=text",
    "weather_realtime": f"{CONFIG['API_BASE']}/v2/weather/realtime"
}

# ==================== 【天气获取模块（60s.viki.moe）】 ====================
def get_current_weather(city_show_name, query_city):
    try:
        params = {"query": query_city}
        res = requests.get(API["weather_realtime"], params=params, timeout=CONFIG["TIMEOUT"])
        res.encoding = "utf-8"
        resp_json = res.json()
        if resp_json.get("code") != 200:
            return f"【{city_show_name}】天气接口返回异常"

        data = resp_json["data"]
        weather = data["weather"]
        air = data["air_quality"]

        warn_text = ""
        alerts = data.get("alerts", [])
        if alerts:
            warn_text = f"\n⚠️预警：{alerts[0]['type']}{alerts[0]['level']} {alerts[0]['detail'][:60]}…"

        output = (
            f"【{city_show_name}】\n"
            f"温度：{weather['temperature']}℃\n"
            f"天气：{weather['condition']}\n"
            f"风力：{weather['wind_direction']}{weather['wind_power']}级\n"
            f"空气质量：{air['quality']} AQI:{air['aqi']}"
        )
        output += warn_text
        return output

    except Exception as e:
        print(f"[天气异常] {city_show_name} : {str(e)}")
        return f"【{city_show_name}】天气获取失败"

# ==================== 【各类信息获取模块】 ====================
def get_fuel_price():
    try:
        res = requests.get(API["fuel"], timeout=CONFIG["TIMEOUT"])
        res.encoding = "utf-8"
        return res.text.strip()
    except Exception as e:
        print(f"[油价异常] {str(e)}")
        return "油价信息获取失败"


def get_moyu():
    try:
        res = requests.get(API["moyu"], timeout=CONFIG["TIMEOUT"])
        res.encoding = "utf-8"
        return res.text.strip()
    except Exception as e:
        print(f"[摸鱼日报异常] {str(e)}")
        return "摸鱼日报获取失败"

# ==================== 【消息组装模块】 ====================
def build_message():
    now = datetime.now()
    week_arr = ["星期一", "星期二", "星期三", "星期四", "星期五", "星期六", "星期日"]
    date_str = now.strftime("%Y-%m-%d")
    week_str = week_arr[now.weekday()]

    weather_content = ""
    for show_name, query_name in CONFIG["CITY_LIST"]:
        weather_content += get_current_weather(show_name, query_name) + "\n\n"

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
    try:
        resp = requests.post(
            CONFIG["WEBHOOK_URL"],
            json=payload,
            timeout=CONFIG["TIMEOUT"]
        )
        resp.raise_for_status()
        print("✅ 推送成功")
    except Exception as e:
        print(f"❌推送失败：{str(e)}")

# ==================== 【主入口】 ====================
if __name__ == "__main__":
    final_msg = build_message()
    print(final_msg)
    send_message(final_msg)
