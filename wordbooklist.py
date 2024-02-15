# -*- coding: utf-8 -*-
"""
Created on Fri Feb  9 06:48:35 2024

@author: dpfka
"""
from re import A
import streamlit as st
import pandas as pd
import os
import re
from io import StringIO
from datetime import datetime
from datetime import timedelta
from streamlit.components.v1 import html

wordbook_path = './단어장 모음'

def make_wordbooks_df(file_list):
    df_wordbooks = pd.DataFrame(columns = ['이름'])
    if len(file_list) == 0:
        return df_wordbooks
    for wb_file in file_list:
        df_wordbooks.loc[len(df_wordbooks)] = wb_file[:-4]
    df_wordbooks = df_wordbooks.sort_values(by='이름', ascending=True).reset_index(drop=True)
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



def make_wordbook(selected_wordbooks, load_user, folder = ""):
    df_words = init_word_df()
    if len(selected_wordbooks) > 0:
        #error_user_wordbooks = []
        if load_user and len(st.session_state['user_wordbook_files']) > 0:#사용자 단어장 불러오기
            for wordbook_name in st.session_state['user_wordbook_files']:
                if wordbook_name[:-4] in list(selected_wordbooks[selected_wordbooks.선택]['이름']):
                    df_wordbook = st.session_state['user_wordbook_files'][wordbook_name]#pd.read_csv(st.session_state['user_wordbook_files'][wordbook_name], encoding='utf-8')
                        
                    # #열 개수 검사
                    # if len(df_wordbook.columns) != 2:
                    #         error_user_wordbooks.append(wordbook_name[:-4])
                    # else:
                        #열 이름 검사
                    if(df_wordbook.columns.tolist() != df_words.columns.tolist()):#열 이름이 형식과 맞지 않으면
                        df_wordbook.columns = df_words.columns
                    df_words = pd.concat([df_words, df_wordbook])
    
        elif (not load_user) and len(list(selected_wordbooks[selected_wordbooks.선택]['이름'])) > 0:#기본 단어장 불러오기
            for wordbook in list(selected_wordbooks[selected_wordbooks.선택]['이름']):
                df_wordbook = pd.read_csv(wordbook_path + '/' + folder + '/' + wordbook+'.csv', encoding='utf-8')
                df_words = pd.concat([df_words, df_wordbook])
    
        # if len(error_user_wordbooks) > 0:
        #     st.error(f"불러오기 실패: 데이터는 한 행이 '단어,뜻'의 두 열로 구성되어야 합니다. 실패 목록 : {', '.join(error_user_wordbooks)}")
        #     return init_word_df()
        # else:
    return df_words

def get_subfolders(folder_path):
    subfolders = []

    # 폴더 내의 모든 파일 및 폴더 목록 가져오기
    items = os.listdir(folder_path)

    for item in items:
        item_path = os.path.join(folder_path, item)

        # 폴더인 경우에만 처리
        if os.path.isdir(item_path):
            subfolders.append(item_path)
            #subfolders.extend(get_subfolders(item_path))  # 재귀적으로 하위 폴더 탐색 : 모든 하위-하위 폴더까지 다 반환

    return subfolders



def show_list(mode="show"):
    #df_words =pd.DataFrame({'단어':['단어를 입력하세요'], '뜻':['뜻1; 뜻2']})
    with st.container():
        st.markdown("#### 기본 단어장 목록")
        
        # 현재 작업 디렉토리의 파일 목록을 가져옴
        folders = get_subfolders(wordbook_path)
        
        #단어장 모음 목록 출력
        #df_folders = pd.DataFrame({'폴더 이름':[folder[folder.find('\\')+1:] for folder in folders], '경로':folders})

        SB_options = []
        pattern = re.compile(r"/([^/]+)$")
        
        for f_path in folders:
            match = pattern.search(f_path)
            SB_options.append(match.group(1))
        
        folder_selected = st.selectbox(
            '단어장 모음 선택',
            sorted(SB_options))
        files = os.listdir( wordbook_path+'/'+folder_selected)
        
        
        # csv를 가진 파일 목록을 필터링하여 반환
        wordbook_files = [file for file in files if file.endswith("csv")]
        
        #단어장 목록 만들기
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
                     disabled = ["이름"],
                     key = "selected_wordbooks"
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
                     disabled = ["이름"],
                     key = "selected_user_wordbooks"
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
        
        #그전에 show_list에서 마지막으로 불러왔던 거 불러오기 위해(화면 표시 유지)
        if mode == 'create':
            df_words = pd.DataFrame({'단어':['단어를 입력하세요'], '뜻':['뜻1; 뜻2']}) if 'df_words' not in st.session_state else st.session_state['df_words']
        elif mode == 'show':
            df_words = init_word_df() if 'df_show' not in st.session_state else st.session_state['df_show']
        
        #선택한 단어장 불러오기
        if load_wordbooks:
            df_words = pd.concat([make_wordbook(selected_wordbooks, False, folder_selected), make_wordbook(selected_user_wordbooks, True)]) 

            if len(df_words) > 0:
                df_words.dropna(subset=['단어','뜻'], inplace = True)
                if del_duplication:
                    df_words = df_words.drop_duplicates(subset=['단어'])
            
                df_words.reset_index(inplace=True, drop=True)
            
                #로드 끝난 후 세션에 저장
                # if mode == 'create':
                #     st.session_state['df_words']  = df_words
                # elif mode == 'show':
                #     st.session_state['df_show']  = df_words
                #st.session_state['last_saved_datetime'] = datetime.now().strftime('%Y-%m-%d %H시 %M분 %S초')
        
        #새로 만들기
        if mode == "create":
            if create_wordbook:
                df_words = pd.DataFrame({'단어':['단어를 입력하세요'], '뜻':['뜻1; 뜻2']})
                
                
                #st.session_state['last_saved_datetime'] = datetime.now().strftime('%Y-%m-%d %H시 %M분 %S초')
        
        #사용자 단어장 삭제
        if del_user_wordbook:
            if len(selected_user_wordbooks) > 0:
                for wordbook in list(selected_user_wordbooks[selected_user_wordbooks.선택]['이름']):
                    st.write(wordbook)
                    del st.session_state['user_wordbook_files'][wordbook+'.csv']
            
                st.rerun()
        
        #로드 끝난 후 세션에 저장
        if mode == 'create':
            st.session_state['df_words']  = df_words
        elif mode == 'show':
            st.session_state['df_show']  = df_words
        
    
    return df_words

#csv 다운로드
@st.cache_data
def convert_df(df:pd.DataFrame):
    # IMPORTANT: Cache the conversion to prevent computation on every rerun
    return df.to_csv(index=False).encode('utf-8')

def make_file_name(name, ext):
    return f"{name} {datetime.now().strftime('%Y-%m-%d %H시 %M분 %S초')}.csv"

# CSV 문자열로 변환
def df_to_txt(df:pd.DataFrame):
    csv_buffer = StringIO()
    df.to_csv(csv_buffer, index=False)
    csv_string = csv_buffer.getvalue()
    return csv_string
