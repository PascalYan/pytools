import os
import requests
import logging
import traceback
from datetime import datetime

class WeChatNotifier:
    def __init__(self):
        self.alert_webhook = os.getenv('WECHAT_ALERT_WEBHOOK')
        if not self.alert_webhook:
            logging.error("企业微信群机器人告警webhook地址未设置！请在.env文件中设置WECHAT_ALERT_WEBHOOK")
            raise ValueError("企业微信群机器人告警webhook地址未设置")
        logging.info("企业微信群机器人通知器初始化完成")

    def send_alert(self, error_msg):
        logging.info("开始发送错误告警...")
        try:
            if isinstance(error_msg, Exception):
                error_type = type(error_msg).__name__
                error_info = str(error_msg)
                stack_trace = traceback.format_exc()
            else:
                error_lines = str(error_msg).split('\n')
                error_type = error_lines[0] if error_lines else "未知错误"
                error_info = error_lines[1] if len(error_lines) > 1 else error_msg
                stack_trace = '\n'.join(error_lines[2:]) if len(error_lines) > 2 else ''
            content = [
                "### GitHub热门项目抓取程序出错",
                f"> 时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
                f"> 错误类型：{error_type}",
                f"> 错误信息：{error_info}"
            ]
            if stack_trace:
                content.append(f"> 错误堆栈：\n{stack_trace}\n")
            data = {
                "msgtype": "markdown",
                "markdown": {
                    "content": "\n".join(content)
                }
            }
            logging.info("正在发送告警消息...")
            response = requests.post(self.alert_webhook, json=data)
            response_json = response.json()
            if response_json.get('errcode', 1) != 0:
                logging.error(f"发送企业微信消息失败: {response.text}")
            else:
                logging.info("告警消息发送成功")
        except Exception as e:
            logging.error(f"发送告警消息时发生错误: {str(e)}")
            raise

    # TODO: 实现 WeChatNotifier 的所有方法和逻辑
    pass 