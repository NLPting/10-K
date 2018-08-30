import glob
from bs4 import BeautifulSoup
import re
import csv
import spacy
import sys
from nltk import sent_tokenize
import pandas as pd
from flashtext import KeywordProcessor
nlp = spacy.load('en_core_web_sm')
keyword_processor = KeywordProcessor(case_sensitive=True)

## 讀取黑白名單
def Load_WhilteBlack(path):
    print('Loading.......white&Black list...............')
    df_e = pd.read_csv(path)
    Ent = []
    for ent , label in zip(df_e['Entity'],df_e['islabel']):
        if label == 1:
            Ent.append(ent)
    Ent =[i.replace('LLC','').replace('Ltd','').replace('Inc','').replace(',','').replace('N.V','').replace('Co.','').replace('.','').strip() for i in Ent]
    for i in Ent:keyword_processor.add_keyword(i)
    return

## 找出含有ORG的句子(使用NER+白名單)
def Have_NER_sentence(Total_sen ,Main_Company , Year):
    Tmp = []
    for s in Total_sen:
        Ent = keyword_processor.extract_keywords(s)
        for e in Ent:
            Tmp.append((s , Main_Company,e , Year))
    return Tmp
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


## 選擇幾家公司
def choose_n_company(i):
    years = ['2012','2013','2014','2015','2016','2017']
    company_list = glob.glob('xxxx/*/')[:i]
    #print(company_list)
    Company_sen = []
    Company_ent = []
    with open('test.sentence.csv','a') as f:
        writer = csv.writer(f)
        writer.writerows([('Sentence','Main','Secondary','Time','Label')])
    for i in company_list:
        print(i)
        for year in years:
            html_list = glob.glob(i+'html/'+year+'*.html')
            Main_Company = html_list[0].split('/')[1]
            Year = html_list[0].split('/')[-1].split('-')[0].replace('.html','')
            #print(Main_Company)
            #print(Year)
            #print(html_list)
            Company_sen = Deal_html_return_sen(html_list)
            Result = Have_NER_sentence(Company_sen,Main_Company,Year)
            with open('test.sentence.csv','a') as f:
                writer = csv.writer(f)
                writer.writerows(Result)
                
                
Load_WhilteBlack('flair.csv')
choose_n_company(5)
print("Finish........")