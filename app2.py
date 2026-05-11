import streamlit as st
import sqlite3
import pandas as pd
import plotly.express as px
import os

# 1. 페이지 설정 및 제목
st.set_page_config(page_title="2024 범죄 데이터 분석 대시보드", layout="wide")
st.title("🚓 공공 데이터 분석: 치안 인프라와 범죄 현황")
st.markdown("이 대시보드는 SQLite 데이터를 바탕으로 지역별 범죄 현황과 치안 요소를 시각화합니다.")

# 2. 데이터베이스 연결 확인 (에러 처리)
db_file = "crime.db"

if not os.path.exists(db_file):
    st.error(f"🚨 '{db_file}' 파일을 찾을 수 없습니다. 데이터베이스 파일이 같은 폴더에 있는지 확인해주세요!")
    st.stop()

# 데이터베이스 연결 함수
def run_query(query):
    with sqlite3.connect(db_file) as conn:
        return pd.read_sql(query, conn)

# --- 시각화 1: CCTV와 절도 발생 ---
st.header("1. CCTV와 절도 발생 관계")
# SQL: CCTV수와 절도를 가져오며, CCTV수가 없는 데이터는 제외합니다.
query1 = """
SELECT 경찰서, CCTV수, 절도 
FROM 최종분석 
WHERE CCTV수 IS NOT NULL
"""
df1 = run_query(query1)

fig1 = px.scatter(df1, x="CCTV수", y="절도", hover_name="경찰서", 
                 title="CCTV 설치 수와 절도 발생 건수 (산점도)",
                 trendline="ols") # 추세선 추가
st.plotly_chart(fig1, use_container_width=True)

st.info("""
**💡 SQL 쿼리:**  
`SELECT 경찰서, CCTV수, 절도 FROM 최종분석 WHERE CCTV수 IS NOT NULL`  
**🔍 인사이트:**  
일반적으로 CCTV가 많은 지역에서 절도 신고가 더 많이 포착되는 경향이 보일 수 있으나, 이는 해당 지역의 인구 밀도가 높거나 유동 인구가 많기 때문일 수 있습니다.
""")


# --- 시각화 2: 관서 수와 범죄 발생 ---
st.header("2. 치안 관서 수와 범죄 발생 현황")
# SQL: 각 관서의 합계를 '관서수'로, 5대 범죄의 합계를 '범죄총합'으로 계산합니다.
query2 = """
SELECT 경찰서, 
       (지구대 + 파출소 + 치안센터) AS 관서수, 
       (살인 + 강도 + 강간추행 + 절도 + 폭력) AS 범죄총합
FROM 최종분석
WHERE 관서수 IS NOT NULL AND 범죄총합 IS NOT NULL
"""
df2 = run_query(query2)

fig2 = px.scatter(df2, x="관서수", y="범죄총합", hover_name="경찰서",
                 title="지역별 관서 수(지구대/파출소/치안센터)와 범죄 발생 총합",
                 color="범죄총합", color_continuous_scale="Reds")
st.plotly_chart(fig2, use_container_width=True)

st.info("""
**💡 SQL 쿼리:**  
`SELECT (지구대+파출소+치안센터) AS 관서수, (살인+강도+강간추행+절도+폭력) AS 범죄총합 FROM 최종분석...`  
**🔍 인사이트:**  
범죄 발생이 많은 지역에 경찰 인프라가 집중되었을 가능성이 있어 단순 인과관계 해석에는 한계가 있습니다. 즉, 관서가 많아서 범죄가 많은 것이 아니라, 범죄 예방을 위해 관서를 많이 배치했을 가능성이 높습니다.
""")


# --- 시각화 3: 범죄 유형별 발생 비율 ---
st.header("3. 범죄 유형별 발생 비중")
# SQL: 각 범죄 컬럼의 전체 합계를 구합니다.
query3 = "SELECT SUM(살인), SUM(강도), SUM(강간추행), SUM(절도), SUM(폭력) FROM 최종분석"
df3 = run_query(query3)
df3.columns = ['살인', '강도', '강간추행', '절도', '폭력']
# 가로로 된 데이터를 세로로 변환
df3_melted = df3.melt(var_name="범죄유형", value_name="발생건수")

fig3 = px.bar(df3_melted, x="범죄유형", y="발생건수", 
             title="전체 범죄 유형별 발생 빈도 비교",
             color="범죄유형", text_auto=True)
st.plotly_chart(fig3, use_container_width=True)

st.info("""
**💡 SQL 쿼리:**  
`SELECT SUM(살인), SUM(강도), SUM(강간추행), SUM(절도), SUM(폭력) FROM 최종분석`  
**🔍 인사이트:**  
전체 범죄 중 폭력과 절도의 비중이 압도적으로 높음을 알 수 있습니다. 살인이나 강도와 같은 강력 범죄는 상대적으로 낮은 비율을 차지하지만, 치안 관리의 핵심 지표로 관리되어야 합니다.
""")

st.caption("Data Source: 2024 경찰청 공공데이터 (가상)")