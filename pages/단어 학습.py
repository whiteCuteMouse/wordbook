# -*- coding: utf-8 -*-
"""
Created on Fri Feb  9 06:44:06 2024

@author: dpfka
"""

import streamlit as st
import re
import pandas as pd
import random
import datetime
import time
import asyncio

import sys

sys.path.append('../')
sys.path.append('../custom_button')
import wordbooklist
import custom_button as cb

#sys.path.append('../practice/component_template_master/component_template_master/template/custom_button/')
#sys.path.append('../practice/')
#import test3
#import __init__
#import custom_button
#from ..practice.component_template_master.component_template_master.template.custom_button import custom_button


try:
   st.set_page_config(
      page_title="단어 학습",
      layout="centered",#centered가 기본값. 고정 너비 안에 element들을 제한. wide는 화면 전체를 사용함.
      initial_sidebar_state="expanded")
except:
   pass

st.title("단어 학습")

#변수 초기화
#화면 구성 변수 초기화
if 'learning' not in st.session_state:
    st.session_state['learning'] = False
if 'test' not in st.session_state:
    st.session_state['test'] = False
if 'test_config' not in st.session_state:
    st.session_state['test_config'] = False
if 'test_result' not in st.session_state:
    st.session_state['test_result'] = False

#데이터 변수 초기화
if 'i' not in st.session_state or 'j' not in st.session_state:
    st.session_state['i'] = 0
    st.session_state['j'] = 0
#if 'df_learning' not in st.session_state:
    #st.session_state['df_learning'] = wordbooklist.init_word_df()
    #st.session_state['df_test'] = wordbooklist.init_word_df()
#df_learning : 선택한 단어장들로부터 불러온 데이터
#df_test : df_learning으로부터 개수 등을 선택하여 시험을 볼 데이터
#df_problems : df_test로부터 문제를 만든 것(n지선다, 정답, 사용자 정답 정보 포함)
#answer_sheet : 결과 출력 화면에서 df_problems 등을 활용해 문제, 뜻, 정답, 나의 답 순으로 정리한 것

# 단어 카드 함수(rotate_card) 보기 모드 관련 변수
if_test = 0x01
if_result = 0x02
if_learning = 0x04

def sleep_milliseconds(milliseconds):
    seconds = milliseconds / 1000.0
    return asyncio.sleep(seconds, result=None)

# 1000밀리초(1초) 동안 sleep
#sleep_milliseconds(1000)

async def count_time(time_, step = 100):
    # timedelta 객체를 사용하여 입력한 시간만큼 이후의 시간 계산
    if 'end_datetime' not in st.session_state:
        delta = datetime.timedelta(hours=0, minutes=time_.minute, seconds=time_.second)
        st.session_state['end_datetime'] = st.session_state['start_datetime'] + delta
    #xst.write(delta)
    placeholder = st.empty()
    remaining_time = st.session_state['end_datetime'] - datetime.datetime.now()
    remaining_milliseconds = remaining_time.seconds * 1000 + remaining_time.microseconds // 1000 
    #total_milliseconds = (time_.minute * 60 + time_.second) * 1000
    #initial_time = f"{time_.minute:02d}" ":" f"{time_.second:02d}"
    
    while remaining_milliseconds > step and st.session_state['test']:
        remaining_milliseconds -= step
        total_seconds = remaining_milliseconds // 1000
        mm, ss = total_seconds // 60, total_seconds % 60
        ll = remaining_milliseconds - total_seconds * 1000
        
        if total_seconds > 10:
            placeholder.markdown(f"##### 남은 시간 : {mm:02d}:{ss:02d}:{ll:03d}")
        else:
            placeholder.markdown(f"##### :red[남은 시간 : {mm:02d}:{ss:02d}:{ll:03d}]")
        await sleep_milliseconds(step)
    #st.session_state['time_over'] = True
    phase_moving('test_to_result')
    st.rerun()

def make_problems(df_word, nChoice, max_nAnswer):#문제 만들 df, n지선다, 최대 정답 개수
    df_problems = pd.DataFrame(columns=['choice_options', 'correct_answer', 'user_answer'])
    df_word_multiple_meaning = pd.DataFrame(columns=['단어','뜻'])
    
    for index, row in df_word.iterrows():
        multiple_meaning = re.split('\s*;\s*', row['뜻'])
        df_word_multiple_meaning.loc[index] = (row['단어'], multiple_meaning)
        
    for i in range(len(df_word_multiple_meaning)):#문제 만들기
        #정답 번호(인덱스)
        if max_nAnswer > 1 and len(df_word_multiple_meaning['뜻'].iloc[i]) > 1:#정답 개수 여러 개인 경우
            nCorrect = random.randint(1, min(max_nAnswer, len(df_word_multiple_meaning['뜻'].iloc[i])))#정답 개수 랜덤 선택(1~최대 정답 개수/최대 뜻 개수 중 작은 값)        
        else:
            nCorrect = 1
        
        #st.write("aaa", max_nAnswer, len(df_word_multiple_meaning['뜻'].iloc[i]), nCorrect, df_word_multiple_meaning['뜻'].iloc[i])
        #correct는 한 문제의 정답 번호 인덱스 세트(예: 1번 문제의 답이 1, 2라면 {0, 1})
        correct = set(random.sample(range(nChoice), nCorrect))#0부터 nChoice-1(3 또는 4)까지 중 nCorrect개의 수를 무작위로 선택
        
        #n-len(correct)지선다 랜덤 추출(정답 제외)(정답 포함해야 n지선다)
        df_choice_options = df_word_multiple_meaning.drop(axis = 0, index = i).sample(nChoice - len(correct)).reset_index(drop=True)#drop의 axis는 삭제 대상이 행인지 열인지 결정. 0이면 행, 1이면 열.
        
        #정답 포함 n지선다 만들기
        df_nChoice = pd.DataFrame(columns = df_choice_options.columns)
        
        #정답의 의미 중 랜덤으로 n개 뽑기
        correct_idxs = list(range(len(correct)))
        correct_idxs = random.sample(correct_idxs, nCorrect)
        
        for n in range(nChoice):
            if n in correct:
                row_correct = pd.DataFrame([[df_word_multiple_meaning.iloc[i,0], df_word_multiple_meaning.iloc[i,1][correct_idxs.pop()]]], columns=df_choice_options.columns)
                df_nChoice = pd.concat([df_nChoice, row_correct])
            else:
                row_option = pd.DataFrame([[df_choice_options.iloc[0, 0], df_choice_options.iloc[0, 1][0]]], columns=df_choice_options.columns)
                df_nChoice = pd.concat([df_nChoice, row_option])
                df_choice_options = df_choice_options.drop(0).reset_index(drop=True)
        
        df_nChoice.reset_index(drop=True, inplace=True)
        df_problems.loc[i] = [df_nChoice, correct, set()]
        
    return df_problems

def change_button_print(placeholder, n, if_test_if_result):
    #placeholder.empty()
    #사용자 정답 저장 : 저장할 땐 st.session_state['df_problems']로 해야 함
    if if_test_if_result & (if_test | ~if_result):#테스트이지만 결과 보기가 아닐 때만
        if n in st.session_state['df_problems']['user_answer'][st.session_state['i']]:
            st.session_state['df_problems']['user_answer'][st.session_state['i']].remove(n)
        else:
            st.session_state['df_problems']['user_answer'][st.session_state['i']].add(n)
    

#카드 뒤집기(단어, 뜻)
def card_flip(if_test_if_result):
     st.session_state['card_reverse'] = not st.session_state['card_reverse']
    
def change_card(to_next, max_len):
    st.session_state['card_reverse'] = False
    if to_next and st.session_state['i'] < max_len - 1:#다음 카드로
        st.session_state['i'] += 1
    elif not to_next and st.session_state['i'] > 0:#이전 카드로
        st.session_state['i'] -= 1

#카드를 로테이션하는 함수(반환값 없음)
def rotate_card(df_word, if_test_if_result, max_len):
    if if_test_if_result & (if_test | if_result) :
        if st.session_state['quiz_mode'] == '단어':
            st.session_state['face_meaning'] = False
            #st.session_state['j'] = 0
        elif st.session_state['quiz_mode'] == '뜻':
            st.session_state['face_meaning'] = True
            #st.session_state['j'] = 1
    else:
        if 'face_meaning' not in st.session_state:
                st.session_state['face_meaning'] = False
                #st.session_state['j'] = 0
        st.session_state['face_meaning'] = st.toggle('카드 앞면을 뜻으로')
    
    if 'card_reverse' not in st.session_state:
        st.session_state['card_reverse'] = False
    
    st.session_state['j'] = int(st.session_state['face_meaning'] ^ st.session_state['card_reverse'])#배타적 논리합
    #FM CF j(앞=0/뒤=1)
    #F F 0
    #F T 1
    #T F 1
    #T T 0
    
    word_pronounce = df_word.iloc[st.session_state['i'], st.session_state['j']]
    card_height = 100 if if_test_if_result & (if_test | if_result) else 300
    font_size = 25 if if_test_if_result & (if_test | if_result) else 40
    nth_container = 0 if if_test_if_result & if_result else (3 if if_test_if_result & if_test else 4)
    
#         div.st-emotion-cache-0:nth-child(2) > 
    #         div:nth-child(1) > 
    #         div:nth-child(1) > 
    #         div:nth-child(3) > 
    #         div:nth-child(1) > 
    #         div:nth-child(1) > 
    #         div:nth-child(1) > 
    #         div:nth-child(1) > 
    #         button :nth-child(1) 
    #         {{
    #             font-size: {font_size}px;
    #             height: {card_height}px;
    #             display: flex; /* 요소를 플렉스 박스로 지정하여 가운데 정렬하기 위해 필요 */
    #             flex-direction: column; /* 요소를 위에서 아래로 정렬 */
    #             justify-content: center; /* 요소를 flex 방향에서 가운데 정렬 */
    #             align-items: center; /* 요소를 flex 수직 방향에서 가운데 정렬 */
    #         }}

            # div[data-testid="stVerticalBlockBorderWrapper"]:nth-of-type({nth_container})
            # {{
            #     background-color: yellow;
            # }}
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
    
    
    if st.session_state['j']:#뜻 보여주기 위해
        card_label = word_pronounce
    else:#단어 보여주기 위해
        if re.search('(.+)\s+(.+)', word_pronounce):
            word = re.search('(.+)\s+(.+)', word_pronounce).group(1)
            pronounce = re.search('(.+)\s+(.+)', word_pronounce).group(2)
            #wordbooklist.p_write(f"{word}<br>{pronounce}", font_size = 80)
            card_label = f"""{word}  
            {pronounce}"""
        else:
            #wordbooklist.p_write(f"{word_pronounce}", font_size = 80)
            card_label = word_pronounce
        
    with st.container():#단어 카드 보여주기 height = 300
        #card_reverse = st.button(label = card_label, use_container_width=True, on_click=card_flip, args=(if_test_if_result,))
        if if_test_if_result & if_learning:#단어/뜻 보여주기 전환 #테스트나 결과 보기가 아닐 때만
            #{nth_container}
            st.markdown(f"""
                        <style>
                        div[data-testid="stVerticalBlockBorderWrapper"]:nth-of-type({nth_container}) button :first-of-type
                        {{
                            font-size: {font_size}px;
                            height: {card_height}px;
                            display: flex; /* 요소를 플렉스 박스로 지정하여 가운데 정렬하기 위해 필요 */
                            flex-direction: column; /* 요소를 위에서 아래로 정렬 */
                            justify-content: center; /* 요소를 flex 방향에서 가운데 정렬 */
                            align-items: center; /* 요소를 flex 수직 방향에서 가운데 정렬 */
                        }}
                        </style>
                        """,unsafe_allow_html=True)
            
            
            
            #card_reverse = cb.custom_button(label = card_label, type="custom", use_container_width=True, height=f"{card_height}px", font_size=f"{font_size}px", on_click=card_flip, args=(if_test_if_result,))
            card_reverse = st.button(label = card_label, use_container_width=True, on_click=card_flip, args=(if_test_if_result,))
        
            
        elif if_test_if_result & if_test:
            card_reverse = cb.custom_button(label = card_label, type="custom", use_container_width=True, height=f"{card_height}px", font_size=f"{font_size}px")
            # st.markdown(f"""
            #             <style>
            #             div[data-testid="stVerticalBlockBorderWrapper"]:nth-of-type({nth_container}) button :first-of-type
            #             {{
            #                 font-size: {font_size}px;
            #                 height: {card_height}px;
            #                 display: flex; /* 요소를 플렉스 박스로 지정하여 가운데 정렬하기 위해 필요 */
            #                 flex-direction: column; /* 요소를 위에서 아래로 정렬 */
            #                 justify-content: center; /* 요소를 flex 방향에서 가운데 정렬 */
            #                 align-items: center; /* 요소를 flex 수직 방향에서 가운데 정렬 */
            #             }}
            #             </style>
            #             """,unsafe_allow_html=True)
            
            # card_reverse = st.button(label = card_label, use_container_width=True, on_click=card_flip, args=(if_test_if_result,))
        elif if_test_if_result & if_result:
            card_reverse = st.button(label = card_label, use_container_width=True)
        
    if if_test_if_result & (if_test | if_result):
        #with st.container():
            nChoice = int(st.session_state['nChoice'][0])
            #출력할 땐 세션에 저장된 것이 아닌, df_problems로 불러와서 해야 함
            df_problems = st.session_state['df_problems'] if if_test_if_result & if_test else st.session_state['df_problems'][st.session_state['df_problems'].index.isin(df_word.index)].reset_index(drop = True)
            
            
            
            choice_j = int(not bool(st.session_state['j']))
            
            options_bool = [True if n in df_problems.iloc[st.session_state['i'], 2] else False for n in range(nChoice)]
            
            placeholders = [st.empty() for e in range(nChoice)]
            
            #선택지 출력
            for n in range(nChoice):
                with placeholders[n]:
                    button_key = f"{st.session_state['i']}_{n}"
                    options_bool[n] = st.button(df_problems['choice_options'][st.session_state['i']].iloc[n][choice_j], on_click=change_button_print, args = (placeholders[n], n, if_test_if_result), use_container_width = True, key=button_key, type="primary" if options_bool[n] == True else "secondary")
                    
    
    with st.container():
        prev_btn, progress, next_btn = st.columns(3)
        with prev_btn:#prev = 
            if st.session_state['i'] <= 0:
                st.button('◀', disabled = True, on_click=change_card, args=(False, max_len)) 
            else: st.button('◀', on_click=change_card, args=(False, max_len))
        with progress:
            wordbooklist.p_write(f"{st.session_state['i']+1} / {max_len}", font_size = 20)
        with next_btn:#next_ = 
            if st.session_state['i'] >= max_len - 1:
                st.button('▶', disabled = True, on_click=change_card, args=(True, max_len))
            else: st.button('▶', on_click=change_card, args=(True, max_len))
            

def phase_moving(phase):
    if phase == 'test_to_config':
        st.session_state['test'] = False
        del st.session_state['df_test']
        del st.session_state['df_problems']
        #del st.session_state['time_over']
        del st.session_state['card_reverse']
        
        if 'timer' in st.session_state:
            del st.session_state['timer']
        if 'start_datetime' in st.session_state:
            del st.session_state['start_datetime']
        if 'end_datetime' in st.session_state:
            del st.session_state['end_datetime']
            
        #nQuiz, quiz_mode, nChoice, use_timer, multiple_answer는 삭제(del)하지 않음
    
    elif phase == 'test_to_result':
        st.session_state['test_result'] = True
        st.session_state['i'] = 0
        st.session_state['j'] = 0
        if 'timer' in st.session_state:
            del st.session_state['timer']
        if 'start_datetime' in st.session_state:
            del st.session_state['start_datetime']
        if 'end_datetime' in st.session_state:
            del st.session_state['end_datetime']
            
    elif phase == 'learning_to_init':
            st.session_state['learning'] = False
            del st.session_state['face_meaning']
            del st.session_state['suffled_df_learning']
            del st.session_state['card_reverse']
            
    elif phase == 'config_to_test':
        st.session_state['use_timer'] = use_timer #test->config로 와도 초기화하지 않는 변수
        if use_timer:
            if minutes > 0 or seconds >= 10:
                st.session_state['timer'] = datetime.time(0, minutes, seconds)
                st.session_state['start_datetime'] = datetime.datetime.now()
        
                st.session_state['test'] = True
                st.session_state['df_test'] = st.session_state['df_learning'].sample(nQuiz)#임의의 행 n개 뽑기
                st.session_state['df_test'].reset_index(drop=True, inplace=True)
                st.session_state['i'] = 0
                st.session_state['j'] = 0
                #st.session_state['time_over'] = False#이건 타이머 쓰든 안 쓰든 무조건 초기화. 왜냐하면 테스트 종료 간단히 구현 위해.
                
                #test->config로 와도 초기화하지 않는 변수들(df_problems 빼고)
                st.session_state['nQuiz'] = nQuiz
                st.session_state['quiz_mode'] = quiz_mode
                st.session_state['nChoice'] = nChoice
                
                st.session_state['multiple_answer'] = multiple_answer
                
                #df_problems는 초기화
                if multiple_answer:
                    st.session_state['df_problems'] = make_problems(st.session_state['df_test'], int(nChoice[0]), 2)
                else:
                    st.session_state['df_problems'] = make_problems(st.session_state['df_test'], int(nChoice[0]), 1)
            else:
                st.error('타이머는 10초 이상으로 설정해야 합니다!')
        else:
            st.session_state['test'] = True
            st.session_state['df_test'] = st.session_state['df_learning'].sample(nQuiz)#임의의 행 n개 뽑기
            st.session_state['df_test'].reset_index(drop=True, inplace=True)
            st.session_state['i'] = 0
            st.session_state['j'] = 0
            #st.session_state['time_over'] = False#이건 타이머 쓰든 안 쓰든 무조건 초기화. 왜냐하면 테스트 종료 간단히 구현 위해.
            
            #test->config로 와도 초기화하지 않는 변수들(df_problems 빼고)
            st.session_state['nQuiz'] = nQuiz
            st.session_state['quiz_mode'] = quiz_mode
            st.session_state['nChoice'] = nChoice
            
            st.session_state['multiple_answer'] = multiple_answer
            
            #df_problems는 초기화
            if multiple_answer:
                st.session_state['df_problems'] = make_problems(st.session_state['df_test'], int(nChoice[0]), 2)
            else:
                st.session_state['df_problems'] = make_problems(st.session_state['df_test'], int(nChoice[0]), 1)
        
    
    elif phase == 'config_to_init':
        st.session_state['test_config'] = st.session_state['test'] = False
        #tes나 result에서 계속 뒤로 눌러서 config->init 될 수 있으니까
        if 'card_reverse' in st.session_state:
            del st.session_state['card_reverse']
        if 'nQuiz' in st.session_state:
            del st.session_state['nQuiz']
        if 'quiz_mode' in st.session_state:
            del st.session_state['quiz_mode']
        if 'nChoice' in st.session_state:
            del st.session_state['nChoice']
        # if 'time_over' in st.session_state:
        #     del st.session_state['time_over']
        if 'use_timer' in st.session_state:
            del st.session_state['use_timer']
        if 'multiple_answer' in st.session_state:
            del st.session_state['multiple_answer']
            
    elif phase == 'init_to_learning':
        if len(st.session_state['df_learning']) > 0:
            st.session_state['learning'] = True
            st.session_state['suffled_df_learning'] = st.session_state['df_learning'].sample(frac=1)#sample 메서드는 데이터프레임에서 임의의 샘플을 추출하여 새로운 데이터프레임을 반환합니다. frac은 추출할 비율.
            st.session_state['i'] = 0
            st.session_state['j'] = 0
    
    elif phase == 'init_to_config':
        if len(st.session_state['df_learning']) > 0:
            st.session_state['test_config'] = True

###여기부터 실질적 화면 표시
phase_main = st.empty()
phase_control_panel = st.empty()

if st.session_state['learning']:
    with phase_main.container():
        st.markdown("#### 학습")
        rotate_card(st.session_state['suffled_df_learning'], if_learning, len(st.session_state['suffled_df_learning']))
        
    with phase_control_panel.container():
        end_learning = st.button("학습 종료", on_click=phase_moving, args=('learning_to_init',))
        
            
elif st.session_state['test_config']:
    if st.session_state['test']:
        if st.session_state['test_result']:
            with phase_main.container():
                st.markdown("#### 테스트 결과")#result phase
                #정답 개수 세기
                nCorrect = (st.session_state['df_problems']['correct_answer'] == st.session_state['df_problems']['user_answer']).sum()
                nWrong = st.session_state['nQuiz'] - nCorrect
                st.markdown(f"##### 정답 : {nCorrect} 개 / {st.session_state['nQuiz']} 개")
                st.markdown(f"##### 정답률 : {nCorrect/st.session_state['nQuiz'] * 100:.2f} %")
                
                view_select = st.radio(
                                        "보기 선택",
                                        ['전체', '정답만', '오답만'],
                                        horizontal=True
                                      )
                
                # if 'problems' not in st.session_state:
                #     problems = st.session_state['problems'] = st.session_state['df_test']['단어']#st.session_state['problems'] = [st.session_state['df_problems']['choice_options'][i]['단어'][list(st.session_state['df_problems']['correct_answer'][i])[0]] for i in range(st.session_state['nQuiz'])]
                # else:
                #     problems = st.session_state['problems']
                
                
                if 'answer_sheet' not in st.session_state: # answer_sheet index는 0부터, 정답, 나의 답 index도 0부터
                    answer_sheet = pd.concat([st.session_state['df_test'], st.session_state['df_problems'].iloc[:, 1:]], axis=1)
                    answer_sheet.columns = ['문제', '뜻', '정답', '나의 답']
                    st.session_state['answer_sheet'] = answer_sheet
                else:
                    answer_sheet = st.session_state['answer_sheet']
                
                filtered_answer_sheet = answer_sheet.set_index(pd.Index(range(1, st.session_state['nQuiz']+1)))
                filtered_answer_sheet['정답'] = [[i + 1 for i in lst] for lst in filtered_answer_sheet['정답']]
                filtered_answer_sheet['나의 답'] = [[i + 1 for i in lst] for lst in filtered_answer_sheet['나의 답']]
                if view_select == "정답만":
                    filtered_answer_sheet = filtered_answer_sheet[filtered_answer_sheet['정답'] == filtered_answer_sheet['나의 답']]
                elif view_select == "오답만":
                    filtered_answer_sheet = filtered_answer_sheet[filtered_answer_sheet['정답'] != filtered_answer_sheet['나의 답']]
                
                #st.write(st.session_state['df_problems']['choice_options'][0]['단어'])
                tab1, tab2 = st.tabs(['답안지 보기', '문항 보기'])
                
                with tab1:
                    st.dataframe(filtered_answer_sheet,column_config={
                                    "정답": st.column_config.ListColumn(
                                        width=100
                                        ),
                                    "나의 답":st.column_config.ListColumn(
                                        width=100
                                        ),
                                })
                with tab2:
                    if view_select == "전체":
                        rotate_card(st.session_state['df_test'], if_result, st.session_state['nQuiz'])
                    elif view_select == "정답만":
                        if st.session_state['i'] > nCorrect-1 and nCorrect > 0:
                            st.session_state['i'] = nCorrect - 1#인덱스가 가질 수 있는 최댓값 = 개수-1
                        
                        if nCorrect > 0:
                            rotate_card(st.session_state['df_test'][answer_sheet['정답'] == answer_sheet['나의 답']], if_result, st.session_state['nQuiz'] - nWrong)
                            st.markdown(f"##### 정답 : {filtered_answer_sheet['정답'].reset_index(drop=True)[st.session_state['i']]}번")
                    elif view_select == "오답만":
                        if st.session_state['i'] > nWrong-1 and nWrong > 0:
                            st.session_state['i'] = nWrong - 1#인덱스가 가질 수 있는 최댓값 = 개수-1
                        if nWrong > 0:
                            rotate_card(st.session_state['df_test'][answer_sheet['정답'] != answer_sheet['나의 답']], if_result, st.session_state['nQuiz'] - nCorrect)
                            st.markdown(f"##### 정답 : {filtered_answer_sheet['정답'].reset_index(drop=True)[st.session_state['i']]}번")
                    
            
            with phase_control_panel.container():
                col_btn1, col_btn2, col_btn3 = st.columns([1, 1, 4])
                with col_btn1:
                    again_test = st.button("다시 하기", key='again_test')
                with col_btn2:
                    go_first = st.button("처음으로", type="primary")
                with col_btn3:
                    st.download_button(
                        label="오답노트 다운로드",
                        data=wordbooklist.convert_df(st.session_state['df_test'][answer_sheet['정답'] != answer_sheet['나의 답']]),
                        file_name=f"오답노트 {datetime.datetime.now()}.csv",
                        mime='text/csv',
                        type="primary"
                    )
                
            
            if again_test:
                st.session_state['test'] = False
                st.session_state['test_result'] = False
                del st.session_state['df_test']
                del st.session_state['df_problems']
                #del st.session_state['problems']
                del st.session_state['answer_sheet']
                #del st.session_state['time_over']
                st.rerun()
            
            if go_first:
                st.session_state['test'] = st.session_state['test_result'] = False
                del st.session_state['df_test']
                del st.session_state['df_problems']
                #del st.session_state['problems']
                del st.session_state['answer_sheet']
                #del st.session_state['time_over']
                
                #테스트 구성 시 살아 있어야 하는 변수들
                st.session_state['test_config'] = st.session_state['test'] = False
                del st.session_state['nChoice']
                del st.session_state['nQuiz']
                del st.session_state['quiz_mode']
                st.rerun()
        else:
            with phase_main.container():
                st.markdown("#### 테스트")#test phase
                
                rotate_card(st.session_state['df_test'], if_test, st.session_state['nQuiz'])
            
            
            with phase_control_panel.container():
                col_btn1, col_btn2 = st.columns([1, 5])
                with col_btn1:
                    back_to_config = st.button("뒤로 가기", key='back_to_config', on_click = phase_moving, args = ('test_to_config',))
                    
                with col_btn2:
                    end_test = st.button("테스트 종료", type="primary", on_click = phase_moving, args=('test_to_result',))
            
            #if st.session_state['time_over']:
            #    phase_moving('test_to_result')
                
            if 'timer' in st.session_state:
                asyncio.run(count_time(st.session_state['timer'], 99))
            
    else:
        with phase_main.container():
            st.markdown("#### 테스트 구성")#config phase
            len_df = len(st.session_state['df_learning'])
            
            nQuiz = st.slider('문제 개수 지정', 5, len_df, (len_df // 3 if len_df // 3 >= 1 else 1) if 'nQuiz' not in st.session_state else st.session_state['nQuiz'])
            
            quiz_mode_options = ["단어", "뜻"]#, "랜덤"
            
            # if 'quiz_mode' not in st.session_state:
            #     st.session_state['quiz_mode'] = "영어"
            
            quiz_mode = st.radio(
                                "문제 제시",
                                quiz_mode_options,
                                horizontal=True,
                                index = quiz_mode_options.index('단어' if 'quiz_mode' not in st.session_state else st.session_state['quiz_mode'])
                                )
            
            nChoice_options = ['4지선다', '5지선다']
            nChoice = st.radio(
                                "선택지 개수",
                                nChoice_options,
                                horizontal=True,
                                index = 0 if 'nChoice' not in st.session_state else nChoice_options.index(st.session_state['nChoice'])
                                )
            
            use_timer = st.toggle('타이머 사용(10초 이상)', value = False if 'use_timer' not in st.session_state else st.session_state['use_timer'])
            timer_col1, timer_col2, timer_col3 = st.columns([2, 2, 6])
            with timer_col1:
                minutes = st.number_input('tm', disabled = not use_timer, key = "timer_min", label_visibility="collapsed", step=1, value = 3, min_value = 0, max_value = 59, format = "%d")
            
            with timer_col2:
                seconds = st.number_input('ts', disabled = not use_timer, key = "timer_sec", label_visibility="collapsed", step=10, value = 0, min_value = 0, max_value = 59, format = "%d")
            
            multiple_answer = st.toggle('복수 정답', value = True if 'multiple_answer' not in st.session_state else st.session_state['multiple_answer'])
        
        with phase_control_panel.container():
            col_btn1, col_btn2 = st.columns([1, 5])
            with col_btn1:
                back_test = st.button("뒤로 가기", key='back_to_learning_main', on_click=phase_moving, args=('config_to_init',))
            with col_btn2:
                start_test = st.button("테스트 시작", type="primary", on_click=phase_moving, args=('config_to_test',))
else:
    with phase_main.container():
        with st.expander("단어장 선택"):#init phase
            st.session_state['df_learning'] = wordbooklist.show_list()
        st.markdown("#### 미리 보기")
        st.dataframe(st.session_state['df_learning'], hide_index = True,
                    column_config={
                       "단어": st.column_config.TextColumn(
                      width="medium"
                      ),
                        "뜻": st.column_config.TextColumn(
                            width="large"
                            ),
                    }
                    )
    
    with phase_control_panel.container():
        col_btn1, col_btn2 = st.columns([1, 5])
        with col_btn1:
            start_learning = st.button("학습 시작", on_click=phase_moving, args=('init_to_learning',))
        with col_btn2:
            config_test = st.button("테스트 만들기", type="primary", on_click=phase_moving, args=('init_to_config',))
