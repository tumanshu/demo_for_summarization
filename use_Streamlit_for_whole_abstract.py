
import streamlit as st
import requests
import json
import streamlit as st
import spacy

nlp = spacy.load('en_core_web_sm')
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib
from pandas.core.frame import DataFrame

matplotlib.use("Agg")
from PIL import Image
from wordcloud import WordCloud, STOPWORDS, ImageColorGenerator
# from summarizer import Summarizer
# import folium
import numpy as np
import nltk
from string import digits
import re
from sklearn.feature_extraction.text import CountVectorizer
from nltk.corpus import stopwords  # To Remove the StopWords like "the","in" ect
from nltk.stem import PorterStemmer
from nltk.stem import WordNetLemmatizer
import pyttsx3

# initialisation
engine = pyttsx3.init()
from gtts import gTTS
from comtypes.client import CreateObject

engine = CreateObject("SAPI.SpVoice")
stream = CreateObject("SAPI.SpFileStream")

bertsum_abstract_url = "http://10.141.112.43:1122//get_bertsum_abs_summary_news/"

bertsum_extract_url ="http://10.141.120.118:8886/bertsumext"

seg_url ="http://10.162.43.49:5999/paragraph_seg"

qa_abstract_url = "http://10.141.112.43:1212/get_qa_abs_summary"
punc=["?","!", "。", "！","？"]

headers = {"Content-Type": "application/json"}
st.write(
    '<style>div.Widget.row-widget.stRadio > div{flex-direction:row;}.header{padding: 10px 16px; background: #111; color: #fff; position:fixed;top:0;text-align: justify;} .sticky { position: fixed; top: 0; width: 100%;}</style>',
    unsafe_allow_html=True)



st.markdown("""
<style>
body {
    color: #111;
    background-color: #eaf4ff  ;


    etc. 
}
</style>

    """, unsafe_allow_html=True)


def get_segment(docx):
    segs = []
    result_long = requests.post(seg_url, json={"doc":docx}, headers=headers)
    text = json.loads(result_long.text)["output"]
    for seg in text:
        segs.append(seg["1-session"])
    return segs


def sumy_abs_summarizer(segs, min_length, max_length):
    min_length = int(min_length*len("".join(segs))/len(segs))
    max_length = int(max_length*len("".join(segs))/len(segs))
    bertsum_abs_result_response = requests.post(bertsum_abstract_url+"?min_length="+str(min_length)+"&max_length="+str(max_length), json=segs, headers=headers)
    bertsum_result_abstract_list = json.loads(bertsum_abs_result_response.text)["final_result"]
    print(bertsum_result_abstract_list)
    return bertsum_result_abstract_list

def sumy_ext_summarizer(segs, min_length, max_length):

    bertsum_ext_result_response = requests.post(bertsum_extract_url, json=segs, headers=headers)
    bertsum_exctract_result_list = json.loads(bertsum_ext_result_response.text)
    real_max = int(len("".join(segs))*max_length)
    final_ext = ""
    final_ext_length = 0
    for ext in bertsum_exctract_result_list:
        if final_ext_length+ext[0][1] >real_max:
            break
        else:
            final_ext += ext[0][0]
            final_ext_length+=ext[0][1]

    return final_ext

def getqa_summary(segs, min_length, max_length):

    text = ["".join(segs).strip().replace("\n","")]
    qa_result_response = requests.post(qa_abstract_url, json=text, headers=headers)
    qa_result_abstract = json.loads(qa_result_response.text)
    #print(qa_result_abstract)
    qa_result_abstract_list = []
    str_ = ""
    result = qa_result_abstract
    if qa_result_abstract[0] == "无":
        qa_result_abstract=text[0]
    for char in qa_result_abstract:
        if len("".join(qa_result_abstract_list))>max_length*len(text[0]):
            break
        str_ += char
        if char in punc:
            qa_result_abstract_list.append(str_)
            str_ = ""
    #print(result)
    if result[0] == "无":
        return qa_result_abstract_list[:1]


    return qa_result_abstract_list



def main():
    # st.sidebar.title("About")
    if st.sidebar.checkbox("相关信息"):
        st.sidebar.info(
            "摘要的展示页面，输入文本，输出分段摘要或者全文摘要"
        )

    st.write(
        '<style>body { margin: 0; font-family: font-family: Tangerine;font-size:48px, Helvetica, sans-serif;font-size: 30px;text-align: justify;} .header{padding: 10px 16px; background: #eaf4ff; color: #111; position:fixed;top:0;text-align: center;} .sticky { position: fixed; top: 0; width: 100%;} </style><div class="header" id="myHeader">' + str(
            '全文摘要展示demo') + '</div>', unsafe_allow_html=True)
    # st.title("Summary Generator and Entity checker")

    raw_text = st.sidebar.text_area("输入文章", height=500)

    summary_min_length = st.sidebar.slider("摘要最小占比", 0.0, 0.5, 0.1, step=0.1)
    summary_max_length = st.sidebar.slider("摘要最大占比", 0.0, 0.5, 0.3, step=0.1)
    if st.sidebar.button("查看摘要"):
        segs = get_segment(raw_text)
        print(len(segs))
        bertsum_abs_summary_result = sumy_abs_summarizer(segs, summary_min_length, summary_max_length)
        bertsum_ext_summary_result = sumy_ext_summarizer(segs, summary_min_length, summary_max_length)
        qa_summary_result = getqa_summary(segs, summary_min_length, summary_max_length)

        # 将结果集成成表格
        st.info("BertSum生成摘要：")
        st.write("".join(bertsum_abs_summary_result))
        st.info("BertSum抽取摘要：")
        st.write(bertsum_ext_summary_result)
        st.info("关系型抽取摘要：")
        st.write("".join(qa_summary_result))

        #st.table(pd_frame)



if __name__ == '__main__':
    main()





