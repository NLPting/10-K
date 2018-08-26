from bs4 import BeautifulSoup
import glob
import re
import csv
import spacy
import sys
from nltk import sent_tokenize
import pandas as pd
from flashtext import KeywordProcessor
nlp = spacy.load('en_core_web_sm')
keyword_processor = KeywordProcessor(case_sensitive=True)

    
    
## 處理特殊狀況的句子
def Filter_Title(sen):
    flag = False
    doc = nlp(sen)
    for token in doc:
        if token.pos_=='VERB':
            flag = True
    return flag

## 前處理(過濾表格、圖、標題)
def Deal_html_return_sen(html_list):
    ## NLTK句子切割
    def nltk_sentence_token(Content):
        Sen= []
        sen_token = sent_tokenize(Content)
        for sen in sen_token:
            if len(sen.split(' '))>=5 and Filter_Title(sen):
                Sen.append(sen)
        return Sen
    ## 處理特殊狀況的句子
    def Filter_Title(sen):
        flag = False
        doc = nlp(sen)
        for token in doc:
            if token.pos_=='VERB':
                flag = True
        return flag
    Sen = []
    for path_html in html_list:
        file = open(path_html , 'r')
        soup = BeautifulSoup(file , 'html.parser')
        file.close()
        tmpp = soup.find_all('p')
        After_filter_title_sen = [i.text.strip() for i in tmpp if i.text and len(i.text.split(' '))>=6 and Filter_Title(i.text)]
        Content = ' '.join(After_filter_title_sen)
        Sen+=nltk_sentence_token(Content)
    return Sen

## 讀取黑白名單
def Load_WhilteBlack(path):
    print('Loading.......white&Black list...............')
    df_e = pd.read_csv(white_black)
    Ent = []
    for ent , label in zip(df_e['Entity'],df_e['islabel']):
        if label == 1:
            Ent.append(ent)
    Ent =[i.replace('LLC','').replace('Ltd','').replace('Inc','').replace(',','').replace('N.V','').replace('Co.','').replace('.','').strip() for i in Ent]
    for i in Ent:keyword_processor.add_keyword(i)
    return

## 找出含有ORG的句子(使用NER+白名單)
def Have_NER_sentence(Total_sen):
    Tmp = []
    for s in Total_sen:
        Ent = keyword_processor.extract_keywords(s)
        for e in Ent:
            Tmp.append((s , Main_Company,e , Year))
    return Tmp

## 吃cmd line 參數 (公司、年份、白名單)
html_fold = sys.argv[1]
year = sys.argv[2]
white_black = sys.argv[3]
html_list = glob.glob(html_fold+year+"*.html")

## 處理後共有幾個句子(尚未用NER)
Total_sen = Deal_html_return_sen(html_list)
print('Have : ',len(Total_sen))

## 友善提醒有沒有抓對正確的年份跟公司
Main_Company = html_list[0].split('/')[1]
Year = html_list[0].split('/')[-1].split('-')[0].replace('.html','')
print('Company : ' , Main_Company)
print('Year : ' , Year)

#導入白名單
Load_WhilteBlack(white_black )
#使句子含有ORG
Result = Have_NER_sentence(Total_sen)

print('Have : ',len(Result))

#將含有ORG的句子、公司、公司對應的公司(NER)、年份及關係存下來       
import csv
with open('test.sentence.csv','w') as f:
    writer = csv.writer(f)
    writer.writerows([('Sentence','Main','Secondary','Time','Label')])
    writer.writerows(Result)
    
    
print('Sucess!!')
