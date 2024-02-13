import streamlit as st
import pandas as pd
import re

try:
   st.set_page_config(
      page_title="단어 공부 앱",
      page_icon="📝",
      layout="centered",#centered가 기본값. 고정 너비 안에 element들을 제한. wide는 화면 전체를 사용함.
      initial_sidebar_state="expanded")
except:
   pass

#with st.sidebar:
#    st.header("메뉴")

st.title("단어 공부 앱")
with st.container():
    st.markdown("""- #### 간단한 단어 공부 앱입니다.""")
    st.markdown("""- #### 나만의 학습장을 만들어 단어를 공부하고, 시험을 볼 수 있습니다.""")
    st.markdown("""- #### 미리 만든 학습장을 업로드하여 시험을 보거나 단어장을 만들 수 있습니다.""")
    st.markdown("""- #### 오답노트를 다운로드할 수 있습니다.""")
    st.markdown("""- #### 기본 단어장은 천천히 추가될 예정입니다.""")
    st.markdown("""- ###### 문의 : dpfka357@naver.com""")