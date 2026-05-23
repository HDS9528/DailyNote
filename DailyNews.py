# -*- coding: utf8 -*-
import requests
from datetime import datetime

# ==================== 【中心化配置】 ====================
CONFIG = {
    "WEBHOOK_URL": "https://qyapi.weixin.com/cgi-bin/webhook/send?key=f1d36ecd-288b-4531-a7fd-47da8db862ec",
    "API_BASE": "https://60s.viki.moe",
    "TIMEOUT": 10
}

# 唯一接口：60秒读懂世界（图片）
API = {
    "news_image": f"{CONFIG['API_BASE']}/v2/60s?encoding=image"
}

# ==================== 【获取60秒图片新闻】 ====================
def get_60s_image():
    try:
        res = requests.get(API["news_image"], timeout=CONFIG["TIMEOUT"])
        res.encoding = "utf-8"
        return res.text.strip()
    except:
        return "60秒读懂世界获取失败"

# ==================== 【组装消息】 ====================
def build_message():
    now = datetime.now()
    week_arr = ["星期一", "星期二", "星期三", "星期四", "星期五", "星期六", "星期日"]
    date_str = now.strftime("%Y-%m-%d")
    week_str = week_arr[now.weekday()]

    content = get_60s_image()

    msg = f"""
****** {date_str} {week_str} ******

{content}
"""
    return msg

# ==================== 【企业微信推送】 ====================
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
