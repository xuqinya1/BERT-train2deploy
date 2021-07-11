#!/usr/bin/env python3
# coding:utf-8

"""
 @Time    : 2019/2/28 15:31
 @Author  : xmxoxo (xmhexi@163.com)
 @File    : tran_service.py
"""
import argparse
import flask
import logging
import json
import os
import re
import sys
import string
import time
import numpy as np

from bert_base.client import BertClient


# 切分句子
def cut_sent(txt):
    # 先预处理去空格等
    txt = re.sub('([　 \t]+)', r" ", txt)  # blank word
    txt = txt.rstrip()  # 段尾如果有多余的\n就去掉它
    nlist = txt.split("\n")
    nnlist = [x for x in nlist if x.strip() != '']  # 过滤掉空行
    return nnlist

##将输入的文本的标点符号给取出来
def add_labels(list_text):
    sentence_labels_list = []###所有句子的带有标点的嵌套list  [[句子1.。。],[句子2.。。],...]
    labels = ['.', ',', '!', '?', '\'']
    for i in range(len(list_text)):

        strip_sentence=list_text[i].strip()##去掉句子里的空白的字符
        # print(strip_sentence)
        strip_sentence_list=strip_sentence.split()
        one_sentence_list=[]  ##一句话的list
        for j in range(len(strip_sentence_list)):
            if strip_sentence_list[j][len(strip_sentence_list[j])-1] in labels:###单词是末尾
                one_sentence_list.append(strip_sentence_list[j][0:len(strip_sentence_list[j])-1])##最后的单词
                one_sentence_list.append(strip_sentence_list[j][len(strip_sentence_list[j])-1])##句末标点
            else:##非句子末尾
                one_sentence_list.append(strip_sentence_list[j])
        sentence_labels_list.append(one_sentence_list)
    return sentence_labels_list

def addTokenColors(tokens,pred_label):
    addColorSrting=''
    oneParagraphString=''
    for i in range(len(tokens)):
        paragraph=tokens[i]
        last_word = ''
        last_entity = ''
        new_word = ''
        new_entity = ''
        oneParagraphString = ''
        underline=0###开关变量，判断句子是否需要添加下划线，暂时这样以后修改
        for j in range(len(paragraph)):
            # print(paragraph[j])
            if paragraph[j]!='[SEP]' and paragraph[j]!='[CLS]':
                ###这里本来是想表达的是：不需要分解的字符串，但是其实是不对的，像有些符号，如()、-等，都是X标签，都是分解的，但没有##
                if not paragraph[j].startswith("##") and not pred_label[i][j] == 'X':  ###不是以##开头的真实
                    if j>0:
                        last_entity=new_entity
                        last_word=new_word
                        new_word=paragraph[j]
                        new_entity=pred_label[i][j]
                        # print(last_word,'  333 ',last_entity)
                        if last_entity.__contains__('CMP'):
                            oneParagraphString += '<font color = "#FF0000" >'
                            oneParagraphString += last_word
                            oneParagraphString += '</font>'
                            oneParagraphString += ' '
                        if last_entity.__contains__('MTH'):
                            oneParagraphString += '<font color = "#FFFF00" >'
                            oneParagraphString += last_word
                            oneParagraphString += '</font>'
                            oneParagraphString += ' '
                        if last_entity.__contains__('SVN'):
                            oneParagraphString += '<font color = "#00FFFF" >'
                            oneParagraphString += last_word
                            oneParagraphString += '</font>'
                            oneParagraphString += ' '
                        if last_entity.__contains__('BON'):
                            oneParagraphString += '<font color = "#F200F2" >'
                            oneParagraphString += last_word
                            oneParagraphString += '</font>'
                            oneParagraphString += ' '
                        if last_entity.__contains__('RCT'):
                            oneParagraphString += '<font color = "#FFA500" >'
                            oneParagraphString += last_word
                            oneParagraphString += '</font>'
                            oneParagraphString += ' '
                        if last_entity.__contains__('ENG'):
                            oneParagraphString += '<font color = "#22ff00" >'
                            oneParagraphString += last_word
                            oneParagraphString += '</font>'
                            oneParagraphString += ' '
                        if last_entity.__contains__('EGVL'):
                            # oneParagraphString += '<font color = "#0131A7" >'
                            oneParagraphString += '<font color = "#FF3399" >'
                            oneParagraphString += last_word
                            oneParagraphString += '</font>'
                            oneParagraphString += ' '
                            underline=1
                        if last_entity.__contains__('O'):
                            oneParagraphString += last_word
                            oneParagraphString += ' '
                    else:
                        new_word=paragraph[j]
                        new_entity=pred_label[i][j]
                else:
                    if paragraph[j].__contains__('##'):
                        stripToken=paragraph[j].replace('##','')
                        new_word+=stripToken
                    else:
                        new_word +=paragraph[j]
                    # print(paragraph[j])
            # print(oneParagraphString,'   222')
        if underline==0:
            addColorSrting+=oneParagraphString
            addColorSrting+='<br>'
        else:
            addColorSrting +='<u>'
            addColorSrting += oneParagraphString
            addColorSrting += '</u>'
            addColorSrting += '<br>'
    print(addColorSrting,'   !!!')
    return addColorSrting


# 对句子进行预测识别
def ner_pred(list_text):
    # 文本拆分成句子
    # list_text = cut_sent(text)
    print("total setance: %d" % (len(list_text)))
    print(list_text,'   list_text')
    with BertClient(ip='0.0.0.0', port=5575, port_out=5576, show_server_config=False, check_version=False,
                    check_length=False, timeout=10000, mode='NER') as bc:
        start_t =time.perf_counter()
        print('list_text:  ',list_text)
        result = bc.encode(list_text, is_tokenized=False)

        print('time used:{}'.format(time.perf_counter() - start_t))

    result_txt = [result[i] for i in range(len(result))]
    result_dict = {}
    for i in range(len(result)):
        # print(result[i])   ###将[{}]中，被[]括起来的{}拿出来
        result_dict = result[i]
    return result_dict
    ##################################测试代码################################



def flask_server(args):
    pass
    from flask import Flask, request, render_template, jsonify

    app = Flask(__name__)

    # from app import routes

    @app.route('/')
    def index():
        return render_template('index.html', version='V 0.1.3')

    @app.route('/api/v0.1/query', methods=['POST'])
    def query():
        res = {}
        txt = request.values['text']
        if not txt:
            res["result"] = "error"
            return jsonify(res)
        lstseg = cut_sent(txt)
        print('-' * 30)
        print('结果,共%d个句子:' % (len(lstseg)))
        for x in lstseg:
            print("第%d句：【 %s】" % (lstseg.index(x), x))
        print('-' * 30)
        if request.method == 'POST' or 1:
            result_dict = ner_pred(lstseg)
        print('result:    ', result_dict)
        final=addTokenColors(result_dict['tokens'], result_dict['pred_label'])

        return final

    app.run(
        host=args.ip,  # '0.0.0.0',
        port=args.port,  # 8910,
        debug=True
    )


def main_cli():
    pass
    parser = argparse.ArgumentParser(description='API demo server')
    parser.add_argument('-ip', type=str, default="127.0.0.1",
                        help='chinese google bert model serving')
    parser.add_argument('-port', type=int, default=8910,
                        help='listen port,default:8910')

    args = parser.parse_args()

    flask_server(args)


if __name__ == '__main__':
    main_cli()