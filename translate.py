#!/usr/bin/python
# -*- coding: UTF-8 -*-
import hashlib
import random
import urllib.parse
import requests

from tkinter import *
from tkinter.filedialog import askdirectory
from tkinter.filedialog import askopenfilename
from concurrent import futures
from io import StringIO

from pdfminer.pdfinterp import PDFResourceManager
from pdfminer.pdfinterp import process_pdf
from pdfminer.converter import TextConverter
from pdfminer.layout import LAParams

def selectPath():
    path_ = askdirectory()
    path.set(path_)
    
def selectPDF():
    pdf_ = askopenfilename(filetypes = [('PDF', '.pdf')])
    pdf.set(pdf_)
    
def read_from_pdf(file_path):
    '''
    解析pdf文件
    '''
    with open(file_path, 'rb') as file:
        resource_manager = PDFResourceManager()
        return_str = StringIO()
        lap_params = LAParams()
        device = TextConverter(
            resource_manager, return_str, laparams=lap_params)
        process_pdf(resource_manager, device, file)
        device.close()
        content = return_str.getvalue()
        return_str.close()
        return content

def create_sign(q, appid, salt, key):
    '''
    制造签名
    '''
    sign = str(appid) + str(q) + str(salt) + str(key)
    md5 = hashlib.md5()
    md5.update(sign.encode('utf-8'))
    return md5.hexdigest()


def create_url(q, url):
    '''
    根据参数构造query字典
    '''
    fro = 'auto'
    to = 'zh'
    salt = random.randint(32768, 65536)
    appid=20180707000183457
    key='_Ua8wuHlAvd0X3DoU4x4'
    sign = create_sign(q, appid, salt, key)
    url = url+'?appid='+str(appid)+'&q='+urllib.parse.quote(q)+'&from='+str(fro)+'&to='+str(to)+'&salt='+str(salt)+'&sign='+str(sign)
    return url


def translate(q):
    url = 'http://api.fanyi.baidu.com/api/trans/vip/translate'
    url = create_url(q, url)
    r = requests.get(url)
    txt = r.json()
    if txt.get('trans_result', -1) == -1:
        print('程序已经出错，请查看报错信息：\n{}'.format(txt))
        return '这一部分翻译错误\n'
    return txt['trans_result'][0]['dst']


def clean_data(data):
    '''
    将输入的data返回成为段落组成的列表
    '''
    data = data.replace('\n\n', '闲谈后')
    data = data.replace('\n', ' ')
    return data.split('闲谈后')


def _main(pdf_path, txt_path):
    # try:
    data = read_from_pdf(pdf_path)
    data_list = clean_data(data)
    with futures.ThreadPoolExecutor(20) as excuter:
        zh_txt = excuter.map(translate, data_list)
    # zh_txt = [translate(txt) for txt in data_list]
    zh_txt = list(zh_txt)
    article = '\n\n'.join(zh_txt)
    print(article)
    with open(txt_path, 'w', encoding='utf-8') as f:
        f.write(article)
    # except Exception:
    #     return -1
    
def triggerTranslate():
    char_pdf='.pdf'
    pdfName=pdf.get()
    #print(pdfName)
    mPos=find_last(pdfName, '/')
    #print(mPos)
    nPos=find_last(pdfName, char_pdf)
    #print(nPos)
    #print (pdfName[mPos+1:nPos])
    coreName=pdfName[mPos:nPos]
    txt_path=path.get() + coreName + ".txt"
    pdfName=pdfName.replace('/','\\')
    txt_path=txt_path.replace('/','\\')
    #appid = 20180707000183457    #填入你的 appid ，为int类型
    #key = '_Ua8wuHlAvd0X3DoU4x4'      #填入你的 key ，为str类型
    print(pdfName)
    print(txt_path)
    _main(pdfName, txt_path)
    #if path.strip()=='':
    #    print ('尚未选择 翻译结果文本保存路径，请先点击 路径选择 按钮进行选择')
    #print(1)
    
def find_last(string,str):
    last_position=-1
    while True:
        position=string.find(str,last_position+1)
        if position==-1:
            return last_position
        last_position=position

root = Tk()
root.title("袁海汐的翻译工具")
path = StringVar()
pdf = StringVar()

Label(root,text = "pdf路径:").grid(row = 0, column = 0)
pdfEntry = Entry(root, textvariable = pdf, width=100).grid(row = 0, column = 1)
Button(root, text = "pdf选择", command = selectPDF).grid(row = 0, column = 2)


Label(root,text = "翻译结果文本保存路径:").grid(row = 1, column = 0)
Entry(root, textvariable = path, width=100).grid(row = 1, column = 1)
Button(root, text = "路径选择", command = selectPath).grid(row = 1, column = 2)

Button(root, text = "翻译", width=10,command = triggerTranslate).grid(row = 2, column = 1)

root.mainloop()