# BentoBrain: 점심시간 매장 분산 추천 시스템
import streamlit as st
import pandas as pd
import numpy as np
import datetime
from math import radians, cos, sin, asin, sqrt

# -----------------------------
# HELPER FUNCTIONS
# -----------------------------
def haversine(lon1, lat1, lon2, lat2):
    """Calculate the great circle distance between two points on the earth (specified in decimal degrees)"""
    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * asin(sqrt(a))
    r = 6371  # Radius of earth in kilometers
    return c * r

# -----------------------------
# SAMPLE DATA GENERATION
# -----------------------------
@st.cache_data
def load_sample_data():
    # Sample restaurant data
    restaurants = pd.DataFrame({
        'id': [1, 2, 3, 4, 5],
        'name': ['김밥천국', '버거킹', '한솥도시락', '이자카야 하나', '채식마을'],
        'category': ['한식', '양식', '한식', '일식', '비건'],
        'lat': [37.499, 37.500, 37.498, 37.497, 37.496],
        'lng': [127.030, 127.032, 127.028, 127.031, 127.029],
        'bento_score': [3.5, 4.0, 4.2, 4.5, 4.8]
    })

    # Simulated visit log (only last 5 days)
    visit_logs = []
    for rid in restaurants['id']:
        for hour in [11, 12, 13]:
            for dow in range(5):  # Mon to Fri
                visit_logs.append({
                    'restaurant_id': rid,
                    'visit_time': f"2024-04-0{dow+8} {hour}:00:00",
                    'weekday': dow,
                    'hour': hour,
                    'count': np.random.randint(5, 40)
                })
    visit_df = pd.DataFrame(visit_logs)

    return restaurants, visit_df

# -----------------------------
# MAIN STREAMLIT APP
# -----------------------------
st.set_page_config(page_title="BentoBrain 점심 추천 시스템", layout="wide")
st.title("🍱 BentoBrain: 점심시간 매장 분산 추천 시스템")

restaurants, visits = load_sample_data()

# -----------------------------
# USER INPUTS
# -----------------------------
st.sidebar.header("내 점심 선호 입력")
user_lat = st.sidebar.number_input("내 위치 위도", value=37.4985, step=0.0001)
user_lng = st.sidebar.number_input("내 위치 경도", value=127.0305, step=0.0001)
time_slot = st.sidebar.selectbox("점심시간 선택", ['11:00', '12:00', '13:00'])
preferred_category = st.sidebar.multiselect("선호 음식 종류", options=restaurants['category'].unique(), default=['한식', '일식'])

# -----------------------------
# RECOMMENDATION LOGIC
# -----------------------------
hour = int(time_slot.split(':')[0])
dow = datetime.datetime.today().weekday()

merged = visits.merge(restaurants, left_on='restaurant_id', right_on='id')
filtered = merged[(merged['hour'] == hour) & (merged['weekday'] == dow)]

# 거리 계산
distances = restaurants.apply(
    lambda row: haversine(user_lng, user_lat, row['lng'], row['lat']), axis=1)
restaurants['distance_km'] = distances

# 혼잡도 데이터 추가
avg_visits = filtered.groupby('restaurant_id')['count'].mean().reset_index()
avg_visits.columns = ['id', 'avg_count']
restaurants = restaurants.merge(avg_visits, on='id', how='left').fillna(0)

# 추천 점수: 가까울수록 + 선호 음식 + 덜 붐빔
restaurants['score'] = (
    (5 - restaurants['distance_km']) * 0.4 +
    restaurants['bento_score'] * 0.3 +
    (50 - restaurants['avg_count']) * 0.3
)

reco_df = restaurants[restaurants['category'].isin(preferred_category)]
reco_df = reco_df.sort_values(by='score', ascending=False)

# -----------------------------
# DISPLAY RESULTS
# -----------------------------
st.subheader("추천 매장 리스트 🍴")
st.dataframe(reco_df[['name', 'category', 'distance_km', 'avg_count', 'bento_score', 'score']])

# 🔧 위도/경도 컬럼명 맞춰주기
reco_df = reco_df.rename(columns={'lng': 'lon'})
# 지도 표시
st.map(reco_df[['lat', 'lon']])
