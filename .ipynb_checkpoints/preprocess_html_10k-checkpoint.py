from bs4 import BeautifulSoup
import glob
import re
import csv
import spacy
import sys
from nltk import sent_tokenize
import pandas as pd
nlp = spacy.load('en_core_web_lg')
#print(sys.argv)



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


## Flair NER Model
from flair.data import Sentence
from flair.models import SequenceTagger
tagger = SequenceTagger.load('ner')
def sentence_ner(sen):
    sentence = Sentence(sen, use_tokenizer=True)
    tagger.predict(sentence)
    ner_tmp ,ner_words,ner_tags = [],[],[]
    for token in sentence:
        if token.get_tag('ner').find('ORG')>=0:
            ner_words.append(token.text)
            ner_tags.append(token.get_tag('ner'))
    index = 0
    flag = False
    flag_i = False
    for word , tag in zip(ner_words , ner_tags):
        if  tag =='B-ORG':
            flag = True
            ner_tmp.append(word)
        if flag:
            if 'I-ORG' == tag:
                ner_tmp[index] = ner_tmp[index] +' '+ word
                flag_i = True         
        if flag_i:
            if 'E-ORG' == tag:
                ner_tmp[index] = ner_tmp[index] +' '+ word
                flag , flag_i = False , False
                index += 1     
        if tag == 'S-ORG':
            ner_tmp.append(word)
            index+=1
    return ner_tmp


## 讀取黑白名單
def Load_WhilteBlack(path):
    b_list = []
    w_list = []
    df_e = pd.read_csv(path)
    for e , label in zip(df_e['Entity'] , df_e['islabel']):
        e=e.strip().replace('\ue5b8','')
        label = str(label)
        if label=='1':
            w_list.append(e)
        else:
            b_list.append(e) 
    w_list = list(set(w_list))
    b_list = list(set(b_list))
    return (w_list , b_list)

## 句子用黑白名單 + Flair Model後，生出來的新的NER名單(人要去Check)
def Find_NER_In_Sentence_Flair(Total_sen , w_list, b_list):
    from flashtext import KeywordProcessor
    keyword_processor = KeywordProcessor()
    for i in w_list:keyword_processor.add_keyword(i)
    Entity = []
    for s in Total_sen:
        Flair = sentence_ner(s)
        w = keyword_processor.extract_keywords(s)
        total = list(set(w+Flair))
        result = []
        for i in total:
            i=i.replace('(','').replace(')','').replace('"','').strip()
            if i in b_list:
                pass
            if i.split(' ')[0].lower()=='the':
                pass
            else:
                result.append(i)
        result = list(set(result))
        Entity+=result
    Entity = list(set(Entity))
    Entity = [e for e in Entity if e[0].istitle() ]
    T_E = []
    for i in Entity:
        try:
            if i not in b_list:
                if i[-2]==' ':
                    i=i.rstrip('.').strip()+'.'
                    T_E.append(i)
                else:
                    T_E.append(i)
            else:pass
        except:
            pass
    Ent = list(set(T_E))
    return Ent


html_fold = sys.argv[1]
html_list = glob.glob(html_fold+'*.html')[:1]
Total_sen = Deal_html_return_sen(html_list)

print('Deal sentence is OK')
print('Now Save these sentence to Database')
white_Black = sys.argv[2]
w_list , b_list = Load_WhilteBlack(white_Black)
Entity_result = Find_NER_In_Sentence_Flair(Total_sen,w_list,b_list)


with open('Test.sentence.txt','w') as f:
    for i in Entity_result:
        f.write(i+'\n')
    f.close()

