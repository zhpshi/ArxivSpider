#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@Time    : 2021/12/17 22:04:24
@Author  : Zhaopeng SHI
@Email   : zhaopshi@gmail.com
@File    : arxivSpider.py
"""

# here put the import lib
import requests
from bs4 import BeautifulSoup

from email import encoders
from email.header import Header
from email.mime.text import MIMEText
from email.utils import parseaddr, formataddr

import smtplib
import datetime


def spider(target):
    """
    :param target:
    :return:
    """
    # Define the four list
    title_list = []  # generate a list to store the title of papers
    author_list = []
    arxiv_number_list = []
    url_list = []

    # Send requests to the server
    req = requests.get(url=target)
    html = req.text  # get the text form of the HTML

    soup = BeautifulSoup(html, 'html.parser')  # generate a beautiful objective
    dl = soup.find_all('dl')[0]
    '''
    After reading the HTML of arxiv, I find that the each day's paper is stored under 
    the a tag named 'dl'. When I find all 'dls', it will give me a list. 
    The index '0' will give the latest day's paper. 
    '''

    title_dl = dl.find_all('div', class_='list-title mathjax')
    author_dl = dl.find_all('div', class_='list-authors')
    span_list = dl.find_all('span', class_="list-identifier")

    for span in span_list:
        a = span.find_all('a')[0]
        arxiv_number_list.append(a.text.replace('\n', ''))
        url_list.append('https://arxiv.org' + a.get('href'))

    for i in range(len(title_dl)):
        title_list.append(title_dl[i].text.replace('\n', ''))
        author_list.append(author_dl[i].text.replace('\n', ''))
    return title_list, author_list, arxiv_number_list, url_list


def sendMessage(msg, from_addr, password, to_addr, smtp_server):
    try:
        smtp = smtplib.SMTP(smtp_server)  # 如上变量定义的，是qq邮箱
        smtp.login(from_addr, password)  # 发送者的邮箱账号，密码
        smtp.sendmail(from_addr, to_addr, msg.as_string())  # 参数分别是发送者，接收者，第三个不知道
        smtp.quit()  # quit from smtp
        print('success')
    except smtplib.SMTPException as e:
        print('error', e)


def generateMessageString(keywords, title_list, author_list, url_list):
    string = '''<h3>''' + keywords + ''':</h3>'''
    string += '''<p>There are''' + ''' ''' + str(len(title_list)) + ''' ''' + '''papers today'''
    for i in range(len(title_list)):
        string += '''<p>''' + str(i + 1) + '''.''' + '''<a href=''' + url_list[i] + '''>''' + title_list[
            i] + '''</a> <a>''' + '''<br>''' + author_list[i] + '''</a>'''

    return string


def generateMessage(content_string):
    date = '[' + datetime.datetime.now().strftime('%Y-%m-%d') + ']'

    msg = MIMEText('''<html>''' + content_string, 'html', 'utf-8')

    subject = date + 'New papers on Arxiv'  # Subject of the email
    msg['From'] = 'zps'
    msg['To'] = 'you'
    msg['Subject'] = subject

    return msg


def main():
    keys = ['Quantum Gas', 'Atomic Physics']
    urls = ['https://arxiv.org/list/cond-mat.quant-gas/recent', 'https://arxiv.org/list/physics.atom-ph/recent']

    from_addr = '969156012@qq.com'
    password = 'fpvyjegabimhbcdg'
    smtp_server = 'smtp.qq.com'
    to_addr = 'zpshi@link.cuhk.edu.hk'  # The reciver can be a list

    greeting_words = '''<p>Hello!'''
    message_string = greeting_words
    for i in range(len(keys)):
        [title_list, author_list, arxiv_number_list, url_list] = spider(urls[i])
        message_string += generateMessageString(keys[i], title_list, author_list, url_list)
    msg = generateMessage(message_string)
    sendMessage(msg, from_addr, password, to_addr, smtp_server)

    return 0


if __name__ == '__main__':
    main()
