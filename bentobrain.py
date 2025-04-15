import streamlit as st
import pandas as pd
import snowflake.connector

st.set_page_config(page_title="BentoBrain NYC", layout="wide")
st.title("🥡 BentoBrain: NYC 점심 크로스 쇼핑 인사이트")

# Snowflake 연결
conn = snowflake.connector.connect(
    user='DAEOM',
    password='Stonybrookrabit922!',
    account='zedjyie-kfb17624',
    warehouse='COMPUTE_WH',
    role='ACCOUNTADMIN',
    database='FREE_SAMPLE_CROSS_SHOPPING_INSIGHTS__NYC_RESTAURANTS',
    schema='PUBLIC'
)

query = """
SELECT LOCATION_NAME, LATITUDE, LONGITUDE, BRANDS, CITY
FROM SPEND_CROSS_SHOPPING_SAMPLE
WHERE CITY = 'New York'
LIMIT 100;
"""

df = pd.read_sql(query, conn)
st.dataframe(df)

# 지도 표시용 컬럼명 변경
df = df.rename(columns={'LATITUDE': 'lat', 'LONGITUDE': 'lon'})
st.map(df[['lat', 'lon']])
