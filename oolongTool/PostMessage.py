#!/usr/bin/python
# -*- coding: UTF-8 -*-
import argparse
import os
import smtplib
from email.mime.text import MIMEText
from email.utils import formataddr
import yaml
import requests

class Notation(object):
    def __init__(self, *args, **kwargs):
        self._class_name = self.__class__.__name__
        self._user_dir = os.path.expanduser('~')
 
        if "path" in kwargs:
            self._yaml_bind(path=kwargs['path'])
        else:
            self._yaml_bind()

        if len(args) or len(kwargs) :
            self._bind(*args, **kwargs)

    def _bind(self, *args, **kwargs):
        pass

    def _yaml_bind(self, verbose=True, path="",):
        local_path = '{}/{}.yml'.format('./.cluster_secret', self._class_name)
        global_path = '{}/{}.yml'.format(f'{self._user_dir}/.cluster_secret', self._class_name)
        user_path = '{}/{}.yml'.format(f'{path}/.cluster_secret', self._class_name)

        save_dir = False
        if os.path.exists(user_path):
            save_dir = user_path
        elif os.path.exists(local_path):
            save_dir = local_path
        elif os.path.exists(global_path):
            save_dir = global_path

        if save_dir:
            if verbose:
                print("ClusterTools: using config in {}".format(save_dir))
            with open(save_dir, 'r') as f:
                key_data = yaml.load(f, Loader=yaml.FullLoader)
            for key, item in key_data.items():
                setattr(self, key, item)
            return True
        else:
            return False
    
    def _yaml_save(self, local=True, path=""):
        pass
        # for key, value in self.__dict__.items():
        if local:
            save_path = './.cluster_secret'
        else:
            save_path = f'{self._user_dir}/.cluster_secret'

        if not path == "":
            save_path = ""

        if not os.path.exists(save_path):
            os.makedirs(save_path)
        with open('{}/{}.yml'.format(save_path, self._class_name), 'w') as f:
            yaml.dump(self.__dict__, f)
            print('{}/{}.yml'.format(save_path, self._class_name), '  saved!!!')

    def _load_content(content):
        if os.path.exists(content):
            with open(content, 'r') as f:
                data = f.read()
            return data
        else:
            return content
    
    def send(self, title, content="", **kwargs):
        self._send(title=title, content=self._load_content(content), **kwargs)
        # self._yaml_save()
    
    def save(self, path=""):
        self._yaml_save(path)

    @classmethod
    def P(cls, title, content="", verbose=False, **kwargs):
        cls._class_name = cls.__name__
        cls._user_dir = os.path.expanduser('~')
        cls._yaml_bind(cls, verbose=False, path=kwargs.get('path', ''))
        cls._send(cls, title, cls._load_content(content), **kwargs)
        return True
        

    def __call__(self, *args, **kwargs):
        self._send(*args, **kwargs)
 
    def __repr__(self):
        pass
    

class Mail(Notation):
    """使用邮箱的工具类

    Arguments:
        sender: 发送的邮箱
        password: SMTP邮箱口令（一般是奇怪的字符串）
        reciver: 接受的邮箱（可和发送邮箱一样）
        sender_name: 发送者昵称
        reciver_name: 接受者昵称
        host: 使用的邮箱服务器地址
        port: 使用的邮箱服务器开放SMTP服务的端口
    
    Usage:
        mail = Mail(balabala) 
        mail.send(title, content)
    """
    def __init__(self, *args, **kwargs):
        super(Mail, self).__init__(*args, **kwargs)
        # self.sender = "xxxx@qq.com"
        # self.password = "xxxxxx"
        # self.reciver = "xxxx@buaa.edu.cn"
    
    def _bind(self, sender, password, reciver, sender_name="act", reciver_name='reciver', host=False, port=False):
        self.sender = sender
        self.password = password
        self.reciver = reciver
        self.sender_name = sender_name
        self.reciver_name = reciver_name
        if host and port:
            self.config_server(host, port)
    
    def config_server(self, host="smtp.qq.com", port=465):
        self.host = host
        self.port = port
    
    def _send(self, title, content, **kwargs):
        msg = MIMEText(content, 'plain', 'utf-8')
        msg['From'] = formataddr([self.sender_name, self.sender])  # 括号里的对应发件人邮箱昵称、发件人邮箱账号
        msg['To'] = formataddr([self.reciver_name, self.reciver])  # 括号里的对应收件人邮箱昵称、收件人邮箱账号
        msg['Subject'] = title  

        server = smtplib.SMTP_SSL(self.host, self.port)  
        server.login(self.sender, self.password)  
        server.sendmail(self.sender, [self.reciver, ], msg.as_string())  # 括号中对应的是发件人邮箱账号、收件人邮箱账号、发送邮件
        server.quit()  


class Wechat(Notation):
    """使用Server酱的工具类（具体配置请前往[Server酱](https://sct.ftqq.com/upgrade?fr=sc)进行查看)

    Arguments:
        id: Server酱的SendKey
        title_prefix:
        title_suffix:
        content_prefix:
        content_suffix:
    """
    def __init__(self, *args, **kwargs):
        super(Wechat, self).__init__(*args, **kwargs)
    
    def _bind(self, id, title_prefix="", title_suffix="", content_prefix="", content_suffix=""):
        self.id = id
        self.TP = title_prefix
        self.TS = title_suffix
        self.CP = content_prefix
        self.CS = content_suffix
    
    def _send(self, title, content=""):
        data = {"title": self.TP+title+self.TS,
                "desp": self.CP+content+self.CS}
        requests.post("https://sctapi.ftqq.com/{}".format(self.id), data=data)
        return True

def main():
    parser = argparse.ArgumentParser(description="PostMessage")
    parser.add_argument('-s', '--subject')
    parser.add_argument('-c', '--content', default='这是一条空消息')
    parser.add_argument('-t', '--type', default='mail')
    args = parser.parse_args()
    assert args.type in ['wechat', 'mail']
    if args.type == "wechat":
        Wechat.P(args.subject, args.content)
    elif args.type == "mail":
        Mail.P(args.subject, args.content)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="PostMessage")
    parser.add_argument('-s', '--subject')
    parser.add_argument('-c', '--content', default='这是一条空消息')
    parser.add_argument('-t', '--type', default='mail')
    args = parser.parse_args()
    assert args.type in ['wechat', 'mail']
    if args.type == "wechat":
        Wechat.P(args.subject, args.content)
    elif args.type == "mail":
        Mail.P(args.subject, args.content)
