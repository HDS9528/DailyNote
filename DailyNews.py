# -*- coding: utf8 -*-
import requests
from datetime import datetime
import warnings
warnings.filterwarnings("ignore")

# ==================== 【中心化配置】 ====================
CONFIG = {
    "WEBHOOK_URL": "https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=f1d36ecd-288b-4531-a7fd-47da8db862ec",
    "API_BASE": "https://60s.gsyy.help",
    "TIMEOUT": 15
}

# 接口：60秒 + 猫眼 + 微博热搜（均为 text）
API = {
    "news_text": f"{CONFIG['API_BASE']}/v2/60s?encoding=text",
    "maoyan_text": f"{CONFIG['API_BASE']}/v2/maoyan/realtime/movie?encoding=text",
    "weibo_text": f"{CONFIG['API_BASE']}/v2/weibo?encoding=text"
}

# ==================== 获取60秒读懂世界 ====================
def get_60s_news():
    try:
        res = requests.get(API["news_text"], timeout=CONFIG["TIMEOUT"])
        res.encoding = "utf-8"
        return res.text.strip()
    except:
        return "【60秒读懂世界】获取失败"

# ==================== 获取猫眼实时票房 ====================
def get_maoyan_boxoffice():
    try:
        res = requests.get(API["maoyan_text"], timeout=CONFIG["TIMEOUT"])
        res.encoding = "utf-8"
        return res.text.strip()
    except:
        return "【猫眼实时票房】获取失败"

# ==================== 获取微博热搜 ====================
def get_weibo_hot():
    try:
        res = requests.get(API["weibo_text"], timeout=CONFIG["TIMEOUT"])
        res.encoding = "utf-8"
        return res.text.strip()
    except:
        return "【微博热搜】获取失败"

# ==================== 企业微信推送 ====================
def send_message(content):
    payload = {
        "msgtype": "text",
        "text": {"content": content}
    }
    requests.post(CONFIG["WEBHOOK_URL"], json=payload)
    print("✅ 推送成功")

# ==================== 主程序 ====================
if __name__ == "__main__":
    now = datetime.now()
    week_arr = ["星期一", "星期二", "星期三", "星期四", "星期五", "星期六", "星期日"]
    date_str = now.strftime("%Y-%m-%d")
    week_str = week_arr[now.weekday()]

    news = get_60s_news()
    boxoffice = get_maoyan_boxoffice()
    weibo = get_weibo_hot()

    msg = f"""
****** {date_str} {week_str} ******

【60秒读懂世界】
{news}

——————————

【猫眼实时票房】
{boxoffice}

——————————

【微博热搜】
{weibo}
"""
    print(msg)
    send_message(msg)
