# -*- coding: utf-8 -*-
"""
Created on Thu Feb  8 10:13:09 2024

@author: dpfka
"""

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

st.title("단어장 만들기")

df_words = wordbooklist.show_list(mode="create")

with st.container():
    tab1, tab2 = st.tabs(["표로 보기", "텍스트로 보기"])
    with tab1:
        edited_df_words = st.data_editor(df_words, hide_index = True,
                                         num_rows="dynamic", disabled = [],
                                         column_config={
                                             "뜻": st.column_config.TextColumn(
                                                 width="large"
                                                 ),
                                         }
                                         )
        save_words_table = st.button("저장", key="table_save")
        
            
        if save_words_table:
            st.session_state['df_words'] = edited_df_words
            st.session_state['last_saved_datetime'] = datetime.now()
            st.rerun()
        
        st.download_button(
            label="CSV 파일로 다운로드",
            data=wordbooklist.convert_df(st.session_state['df_words']) if 'df_words' in st.session_state else wordbooklist.convert_df(df_words),
            file_name=f"단어장 {datetime.now()}.csv",
            mime='text/csv',
            type="primary"
        )
        
        
        
    with tab2:
        # CSV 문자열로 변환
        def to_txt(df):
            csv_buffer = StringIO()
            df.to_csv(csv_buffer, index=False)
            csv_string = csv_buffer.getvalue()
            return csv_string

        # CSV 문자열 출력
        txt_words = st.text_area(
        "데이터를 텍스트로 보기",
        to_txt(df_words),
        label_visibility = "collapsed",
        height = 350
        )
        save_words_txt = st.button("저장", key="txt_save")
        
        
        if save_words_txt:
            edited_df_words = pd.read_csv(StringIO(txt_words))
            st.session_state['df_words'] = edited_df_words
            st.session_state['last_saved_datetime'] = datetime.now()
            st.rerun()
        
        #txt 다운로드
        st.download_button(
            label="txt 파일로 다운로드",
            data=to_txt(st.session_state['df_words']) if 'df_words' in st.session_state else to_txt(df_words),
            file_name=f"단어장 {datetime.now()}.txt",
            mime='text/csv',
            type="primary"
        )
        
    st.write(f"마지막 저장 : {st.session_state['last_saved_datetime']}")
        
        
        
        
        
with st.container():
    pass
    
    #new_wordbook = st.text_input('새 단어장 이름', '새 단어장', max_chars=20)
    #edited_df_words.to_csv(new_wordbook+'.csv', index=False)
    
    