# -*- coding: utf-8 -*-
"""
Created on Fri Feb  9 06:48:35 2024

@author: dpfka
"""
import streamlit as st
import pandas as pd
import os
from datetime import datetime
from datetime import timedelta
from streamlit.components.v1 import html

def make_wordbooks_df(file_list):
    df_wordbooks = pd.DataFrame(columns = ['이름'])
    if len(file_list) == 0:
        return df_wordbooks
    for wb_file in file_list:
        df_wordbooks.loc[len(df_wordbooks)] = wb_file[:-4]

    #단어장 선택 가능하도록 boolean을 앞에 결합(기본값은 모두 False)
    df_wordbooks = pd.concat([pd.DataFrame([False for n in file_list], columns=['선택']), df_wordbooks], axis = 1)
    return df_wordbooks

#html <p>에 글씨 쓰기
def p_write(txt, font_size = 10, font_weight = "normal", text_align = "center", font_style = "normal", color = "black", writeHTML=True):
    r = f'<p style="font-family:Malgun Gothic; text-align:{text_align}; font-size: {font_size}px; font-weight: {font_weight}; font-style: {font_style}; color: {color}">{txt}</p>'
    if writeHTML:
        st.markdown(r, unsafe_allow_html=True)
    return r
#html <span>에 글씨 쓰기
#span에는 text-align 속성이 없음
def span_write(txt, font_size = 10, font_weight = "normal", font_style = "normal", color = "black", writeHTML = True):
    r = f'<span style="font-family:Malgun Gothic; font-size: {font_size}px; font-weight: {font_weight}; font-style: {font_style}; color: {color}">{txt}</span>'
    if writeHTML:
        st.markdown(r, unsafe_allow_html=True)
    return r

def init_word_df():
    return pd.DataFrame(columns=['단어', '뜻'])

def show_list(mode="show"):
    with st.container():
        st.markdown("#### 기본 단어장 목록")
        
        # 현재 작업 디렉토리의 파일 목록을 가져옴
        files = os.listdir('.')
        # 특정 확장자를 가진 파일 목록을 필터링하여 반환
        wordbook_files = [file for file in files if file.endswith("csv")]
            
        df_wordbooks = make_wordbooks_df(wordbook_files)
        selected_wordbooks = st.data_editor(df_wordbooks, #반환값은 df형
                     hide_index = True,
                     column_config={
                         "선택": st.column_config.CheckboxColumn(
                             ),
                         "이름": st.column_config.TextColumn(
                             "단어장 이름",
                             width="large"
                             )
                         },
                     disabled = ["이름"]
                     )
        
        st.markdown("#### 사용자 단어장 목록")
        if 'user_wordbook_files' not in st.session_state:
            st.session_state['user_wordbook_files'] = {}
        
        uploaded_files = st.file_uploader("CSV 파일 선택", accept_multiple_files=True, type=['csv'])
        
        register_csv = st.button("업로드한 파일 등록")
        if register_csv:
            for uploaded_file in uploaded_files:
                #bytes_data = uploaded_file.read()
                st.session_state['user_wordbook_files'][uploaded_file.name] = pd.read_csv(uploaded_file, encoding='utf-8')
        
        selected_user_wordbooks = st.data_editor(make_wordbooks_df(list(st.session_state['user_wordbook_files'].keys())), #반환값은 df형
                     hide_index = True,
                     column_config={
                         "선택": st.column_config.CheckboxColumn(
                             ),
                         "이름": st.column_config.TextColumn(
                             "단어장 이름",
                             width="large"
                             )
                         },
                     disabled = ["이름"]
                     )
        
        del_duplication = st.checkbox("중복 단어 제거", value=True)
            
        col1, col2, col3 = st.columns(3)
        with col1:
            load_wordbooks = st.button("불러오기")
        with col2:
            if mode == "create":
                create_wordbook = st.button("새로 만들기")
        with col3:
            del_user_wordbook = st.button("사용자 단어장 삭제", type="primary")
            
        
        if 'df_words' not in st.session_state:
            df_words = init_word_df()
        else:
            df_words = st.session_state['df_words']
        
        def make_wordbook(selected_wordbooks, load_user):
            df_words = init_word_df()
            if load_user and len(st.session_state['user_wordbook_files']) > 0:#사용자 단어장 불러오기
                for wordbook_name in st.session_state['user_wordbook_files']:
                    if wordbook_name[:-4] in list(selected_user_wordbooks[selected_user_wordbooks.선택]['이름']):
                        df_wordbook = st.session_state['user_wordbook_files'][wordbook_name]#pd.read_csv(st.session_state['user_wordbook_files'][wordbook_name], encoding='utf-8')
                        df_words = pd.concat([df_words, df_wordbook])
            elif (not load_user) and len(list(selected_wordbooks[selected_wordbooks.선택]['이름'])) > 0:#기본 단어장 불러오기
                for wordbook in list(selected_wordbooks[selected_wordbooks.선택]['이름']):
                    df_wordbook = pd.read_csv(wordbook+'.csv', encoding='utf-8')
                    df_words = pd.concat([df_words, df_wordbook])
            return df_words
        
        #불러오기
        if load_wordbooks:
            df_words = pd.concat([make_wordbook(selected_wordbooks, False), make_wordbook(selected_user_wordbooks, True)])
            
            if del_duplication:
                df_words = df_words.drop_duplicates(subset=['단어'])
            
            df_words.reset_index(inplace=True, drop=True)
            
            #로드 끝난 후 세션에 저장
            st.session_state['df_words'] = df_words
            st.session_state['last_saved_datetime'] = datetime.now()
        
        #새로 만들기
        if mode == "create":
            if create_wordbook:
                df_words = pd.DataFrame({'단어':['단어'], '뜻':['뜻']})
                st.session_state['df_words'] = df_words
                st.session_state['last_saved_datetime'] = datetime.now()
        
        #사용자 단어장 삭제
        if del_user_wordbook:
            if len(selected_user_wordbooks) > 0:
                for wordbook in list(selected_user_wordbooks[selected_user_wordbooks.선택]['이름']):
                    st.write(wordbook)
                    del st.session_state['user_wordbook_files'][wordbook+'.csv']
            
                st.rerun()
        
        
        
        if  'last_saved_datetime' not in st.session_state:
            st.session_state['last_saved_datetime'] = ""
            
    return df_words

#csv 다운로드
@st.cache_data
def convert_df(df):
    # IMPORTANT: Cache the conversion to prevent computation on every rerun
    return df.to_csv(index=False).encode('utf-8')

#https://discuss.streamlit.io/t/is-it-possible-to-read-set-st-session-state-content-in-javascript/45571/2
def style_button(n_element:int, color:str = "", width:int = -1, height:int = -1):
    js = fr'''
    <script>
    // Find all the buttons
    var buttons = window.parent.document.getElementsByClassName("stButton");
    
    // Select only one button
    var button = buttons[{n_element}].getElementsByTagName("button")[0];
    '''
    
    js_btn_color = fr'''
    // Modify its color
    button.style.backgroundColor = '{color}';
    ''' if color != "" else ""
    
    js_btn_width = fr'''
    button.style.width = '{width}';
    ''' if width != -1 else ""
    
    js_btn_height = fr'''
    button.style.height = '{height}';
    ''' if height != -1 else ""
        
    end_js = "</script>"
    js += js_btn_color + js_btn_width + js_btn_height + end_js
    st.components.v1.html(js, width=0, height=0)