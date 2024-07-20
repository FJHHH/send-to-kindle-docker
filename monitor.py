import os
import time
import logging
import smtplib
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart

# 初始化日志配置
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# 获取配置信息
EMAIL_USER = os.environ.get('EMAIL_USER')
EMAIL_PASSWORD = os.environ.get('EMAIL_PASSWORD')
EMAIL_RECEIVER = os.environ.get('EMAIL_RECEIVER')
WATCH_DIR = os.environ.get('WATCH_DIR', '/data/books')
SMTP_SERVER = os.environ.get('SMTP_SERVER')
SMTP_PORT = os.environ.get('SMTP_PORT', 587)  # 读取SMTP端口配置项
SENDED_DIR = os.environ.get('SENDED_DIR', WATCH_DIR + '/sended')

if not os.path.exists(SENDED_DIR):
    os.makedirs(SENDED_DIR)

def send_email(filepath):
    logging.info("send_email filepath: %s", filepath) 
    msg = MIMEMultipart()
    msg['Subject'] = 'File Sent'
    msg['From'] = EMAIL_USER
    msg['To'] = EMAIL_RECEIVER

    # 构建邮件正文
    text = MIMEText("Please find the attached file.")
    msg.attach(text)

    # 添加附件
    with open(filepath, 'rb') as f:
        attachment = MIMEApplication(f.read(), _subtype=os.path.splitext(filepath)[1][1:])
        attachment.add_header('Content-Disposition', 'attachment', filename=os.path.basename(filepath))
        msg.attach(attachment)

    # 发送邮件
    server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
    server.starttls()  # 如果SMTP服务器需要TLS加密
    logging.info("EMAIL_USER: %s", EMAIL_USER) 
    server.login(EMAIL_USER, EMAIL_PASSWORD)
    server.sendmail(EMAIL_USER, EMAIL_RECEIVER, msg.as_string())
    server.quit()

def move_file(src, dst):
    file_name, file_extension = os.path.splitext(os.path.basename(src))
    count = 0
    if os.path.exists(os.path.join(dst, f"{file_name}{file_extension}")):
        count += 1
    while os.path.exists(os.path.join(dst, f"{file_name}({count}){file_extension}")):
        count += 1
    if count == 0:
        dst_file = os.path.join(dst, f"{file_name}{file_extension}")
    else:
        dst_file = os.path.join(dst, f"{file_name}({count}){file_extension}")

    logging.info("move_file src: %s, dst_file: %s", src, dst_file)
    os.rename(src, dst_file)

def monitor_and_send():
    while True:
        time.sleep(120)  # 等待10秒，避免过于频繁的检查
        logging.info("开始遍历目录: %s", WATCH_DIR) 

        for filename in os.listdir(WATCH_DIR):
            filepath = os.path.join(WATCH_DIR, filename)
            logging.info("文件， filename:%s, filepath: %s", filename, filepath)
            if os.path.isfile(filepath):
                try:
                    send_email(filepath)
                    move_file(filepath, SENDED_DIR)
                except Exception as e:
                    logging.error("send_email Exception:%s, filepath: %s", filename, filepath, e)

if __name__ == "__main__":
    monitor_and_send()
