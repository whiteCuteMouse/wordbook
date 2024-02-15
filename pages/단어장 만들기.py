# -*- coding: utf-8 -*-
"""
Created on Thu Feb  8 10:13:09 2024

@author: dpfka
"""

from re import I
import streamlit as st
import pandas as pd
import os
from io import StringIO
from datetime import datetime
import wordbooklist

try:
   st.set_page_config(
      page_title="단어장 만들기",
      page_icon="📝",
      layout="centered",#centered가 기본값. 고정 너비 안에 element들을 제한. wide는 화면 전체를 사용함.
      initial_sidebar_state="expanded")
except:
   pass

if 'load_last_df' not in st.session_state:
    st.session_state['load_last_df'] = False

if  'last_saved_datetime' not in st.session_state:
    st.session_state['last_saved_datetime'] = ""
if 'key_suffix' not in st.session_state:
    st.session_state['key_suffix'] = True


st.title("단어장 만들기")

with st.expander("단어장 선택"):#init phase
    df_words = wordbooklist.show_list(mode="create")


st.write("----------")
with st.container():
    st.markdown(#st-emotion-cache-1umgz6k ef3psqc12  #stVerticalBlockBorderWrapper
                #div[data-testid="stVerticalBlockBorderWrapper"]:nth-of-type({nth_container}) button:first-of-type
        f"""
        <style>
            div[data-testid="column"]:nth-of-type(3) /* div[data-testid="column"]에 적용된 스타일을 가진 모든 버튼의 자식 요소 중에서 첫 번째로 나오는 요소를 선택.  */
            {{
                text-align: end;
            }}
        </style>
        """,unsafe_allow_html=True
        ) 


    st.write("※ 단어의 뜻이 여러 개인 경우 세미콜론(;)으로 구분하세요.")
    edit = st.session_state['toggle_edit'] = st.toggle("수정하기", value=False)
    if edit:
        widget_key = "edit"
        st.write("현재 불러오기가 적용되지 않습니다.")
    else:
        widget_key = "normal"
        st.session_state['edit_df_words'] = df_words

    tab1, tab2 = st.tabs(["표로 보기", "텍스트로 보기"])
    with tab1:
        #표 출력
        # if 'df_words' not in st.session_state:
        #     df_words = st.session_state['df_words'] = loaded_df_words

        #st.session_state['df_words']는 단지 화면 표시 유지를 위한 것
        if st.session_state['load_last_df'] and 'last_df_words' in st.session_state:#<마지막 저장 불러오기> 눌렀을 때
            df_words = st.session_state['edit_df_words'] = st.session_state['last_df_words']
            st.write(f"{st.session_state['last_saved_datetime']} 저장을 불러옴.")
        else:
            df_words = st.session_state['edit_df_words']
        
        
        edited_df_words = st.session_state['df_words'] = st.data_editor(df_words, hide_index = True,
                                            num_rows="dynamic", disabled = not edit,
                                            column_config={
                                                            "뜻": st.column_config.TextColumn(
                                                                width="large"
                                                                ),
                                                        }, key=widget_key + str(st.session_state['key_suffix'])
                                        )
        
        #버튼 출력
        btn_col1, btn_col2, btn_col3 = st.columns(3)
        with btn_col1:
            save_words_table = st.button("저장", key="table_save")
            if save_words_table:
                st.session_state['last_df_words']  = st.session_state['edit_df_words'] = st.session_state['df_words'] = edited_df_words
                st.session_state['last_saved_datetime'] = datetime.now().strftime('%Y-%m-%d %H시 %M분 %S초')
                #st.rerun()
        with btn_col2:
            st.session_state['load_last_df'] = st.button("마지막 저장 불러오기", key="load_save")
            if st.session_state['load_last_df']:
                st.session_state['key_suffix'] = not st.session_state['key_suffix']
                st.rerun()
                
        with btn_col3:
            st.download_button(
                label="CSV 파일로 다운로드",
                data=wordbooklist.convert_df(st.session_state['df_words']) if 'df_words' in st.session_state else wordbooklist.convert_df(df_words),
                file_name=wordbooklist.make_file_name("단어장", "csv"),
                mime='text/csv',
                type="primary"
            )
        
        
    with tab2:
        if st.session_state['load_last_df'] and 'last_df_words' in st.session_state:#<마지막 저장 불러오기> 눌렀을 때
            df_words = st.session_state['edit_df_words'] = st.session_state['last_df_words']
            st.write(f"{st.session_state['last_saved_datetime']} 저장을 불러옴.")
        else:
            df_words = st.session_state['edit_df_words']
        
        # CSV 문자열 출력
        txt_words = st.text_area(
        "데이터를 텍스트로 보기",#레이블은 안 보이게 숨김
        wordbooklist.df_to_txt(df_words),
        label_visibility = "collapsed",
        height = 350,
        key="TA" + widget_key + str(st.session_state['key_suffix']),
        disabled = not edit,
        )


        #버튼 출력
        btn_col1, btn_col2, btn_col3 = st.columns(3)
        with btn_col1:
            save_words_txt = st.button("저장", key="txt_save")
            if save_words_txt:
                edited_df_words = pd.read_csv(StringIO(txt_words))
                st.session_state['last_df_words'] = st.session_state['edit_df_words'] = st.session_state['df_words'] = edited_df_words
                st.session_state['last_saved_datetime'] = datetime.now().strftime('%Y-%m-%d %H시 %M분 %S초')
                st.rerun()



        with btn_col2:
            st.session_state['load_last_df'] = st.button("마지막 저장 불러오기", key="TA_load_save")
            if st.session_state['load_last_df']:
                st.session_state['key_suffix'] = not st.session_state['key_suffix']
                st.rerun()
            
        with btn_col3:
            #txt 다운로드
            st.download_button(
                label="txt 파일로 다운로드",
                data=wordbooklist.df_to_txt(st.session_state['df_words']) if 'df_words' in st.session_state else wordbooklist.df_to_txt(df_words),
                file_name=f"단어장 {datetime.now()}.txt",
                mime='text/csv',
                type="primary"
            )
            

    st.write(f"마지막 저장 : {st.session_state['last_saved_datetime']}")


        
    
