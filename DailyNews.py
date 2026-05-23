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

# 用 text 纯文本接口，不乱码
API = {
    "news_text": f"{CONFIG['API_BASE']}/v2/60s?encoding=text"
}

# ==================== 获取60秒读懂世界（纯文本） ====================
def get_60s_news():
    try:
        res = requests.get(API["news_text"], timeout=CONFIG["TIMEOUT"])
        res.encoding = "utf-8"
        return res.text.strip()
    except:
        return "获取失败"

# ==================== 推送消息 ====================
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
    
    msg = f"""
****** {date_str} {week_str} ******

{news}
"""
    print(msg)
    send_message(msg)
