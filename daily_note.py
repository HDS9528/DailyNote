# -*- coding: utf8 -*-
import requests
from datetime import datetime
import json
import os
import time

# ==================== 【中心化配置模块】 ====================
CONFIG = {
    "WEBHOOK_URL": "https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=33a8f34a-6abe-434a-81ef-bb9a252cc3f1",
    # (显示名称 , query查询城市名)
    "CITY_LIST": [
        ("武平", "武平"),
        ("宁波-镇海", "镇海")
    ],
    "API_BASE": "https://60s.gsyy.help",
    "TIMEOUT": 10,
    "REQ_DELAY": 0.4,
    "OIL_UPDATE_HOUR": 6,
    "OIL_CACHE_FILE": "oil_cache.txt"
}
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36"
}

# ==================== 【天气获取模块】 ====================
def get_current_weather(city_show_name, query_city):
    try:
        params = {"query": query_city}
        res = requests.get(f"{CONFIG['API_BASE']}/v2/weather/realtime", params=params, headers=HEADERS, timeout=CONFIG["TIMEOUT"])
        time.sleep(CONFIG["REQ_DELAY"])
        res.encoding = "utf-8"
        try:
            resp_json = res.json()
        except json.JSONDecodeError:
            print(f"[天气] {city_show_name} 返回非JSON响应")
            return f"【{city_show_name}】天气接口返回异常"
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
    """
    >=OIL_UPDATE_HOUR：请求新油价，成功写入缓存
    <OIL_UPDATE_HOUR：读取缓存昨日油价，附带文字提示
    """
    now = datetime.now()
    hour = now.hour
    cache_path = CONFIG["OIL_CACHE_FILE"]
    if hour >= CONFIG["OIL_UPDATE_HOUR"]:
        try:
            url = f"{CONFIG['API_BASE']}/v2/fuel-price?region=浙江&encoding=text"
            res = requests.get(url, headers=HEADERS, timeout=CONFIG["TIMEOUT"])
            time.sleep(CONFIG["REQ_DELAY"])
            res.encoding = "utf-8"
            oil_text = res.text.strip()
            if oil_text:
                # 更新缓存
                with open(cache_path, "w", encoding="utf-8") as f:
                    f.write(oil_text)
            return oil_text
        except Exception as e:
            print(f"[油价异常] {str(e)}")
            return "油价信息获取失败"
    else:
        # 小于设定小时，读取缓存
        if os.path.exists(cache_path):
            with open(cache_path, "r", encoding="utf-8") as f:
                cache_text = f.read().strip()
            return f"{cache_text}\n⚠️以下为昨日油价，6点后更新今日数据"
        else:
            return "暂无油价缓存，请6点后执行获取最新油价"

def get_moyu():
    """摸鱼日报强制传入本地北京时间日期，不受服务端时区影响"""
    try:
        today_str = datetime.now().strftime("%Y-%m-%d")
        url = f"{CONFIG['API_BASE']}/v2/moyu?encoding=text&date={today_str}"
        res = requests.get(url, headers=HEADERS, timeout=CONFIG["TIMEOUT"])
        time.sleep(CONFIG["REQ_DELAY"])
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
