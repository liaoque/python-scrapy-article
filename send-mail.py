#!/usr/bin/python
# -*- coding: UTF-8 -*-

import smtplib
from email.mime.text import MIMEText
from email.header import Header

# 第三方 SMTP 服务
mail_host = "smtp.sohu.com"
mail_user = "@sohu.com"
mail_pass = ""

sender = '@sohu.com'
receivers = ['@qq.com']  # 接收邮件，可设置为你的QQ邮箱或者其他邮箱

mail_msg = """
123123123123123123123123123113123121123123123123123123123123123113123121123123123123123123123123123113123121
123123123123123123123123123113123121123123123123123123123123123113123121123123123123123123123123123113123121
"""
message = MIMEText(mail_msg, 'plain', 'utf-8')
message['From'] = "<@sohu.com>"
message['To'] = "@qq.com<@qq.com>"

subject = 'liaoque2021'
message['Subject'] = Header(subject, 'utf-8')

try:
    smtpObj = smtplib.SMTP_SSL(mail_host, 465)
    # smtpObj.connect(mail_host, 465)  # 25 为 SMTP 端口号
    smtpObj.login(mail_user, mail_pass)
    smtpObj.sendmail(sender, receivers, message.as_string())
    print("邮件发送成功")

    smtpObj.quit()
except smtplib.SMTPException:
    print("Error: 无法发送邮件")
