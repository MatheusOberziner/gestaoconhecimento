import pandas as pd
import streamlit as st
import datetime as dt

@st.cache_data
def load_database():
  df = pd.read_excel('data/walmart_retail_data.xlsx')
  df['order_date'] = pd.to_datetime(df['order_date'], errors='coerce')
  df['ship_date'] = pd.to_datetime(df['ship_date'], errors='coerce')
  df['Order Year'] = df['order_date'].dt.year
  df['Order Month'] = df['order_date'].dt.month
  df['Ship Year'] = df['ship_date'].dt.year
  df['Ship Month'] = df['ship_date'].dt.month
  df = df.drop(columns=['row_id', 'order_id', 'customer_age', 'number_of_records'])
  return df

st.set_page_config(page_title="Gestão do Conhecimento", layout="wide")
st.session_state['df'] = load_database()
st.session_state['dimensao'] = [
  'customer_segment', 'order_priority', 'ship_mode', 'region', 
  'state', 'city', 'product_category', 'product_sub_category'
]
st.session_state['dimensao_tempo'] = ['Ship Year', 'Ship Month', 'Order Year', 'Order Month',]
st.session_state['medida'] = ['sales', 'profit', 'order_quantity']
st.session_state['agregador'] = ['sum', 'mean', 'count', 'min', 'max']
st.title('Gestão do Conhecimento')

pg = st.navigation(
  {
    "Introdução": [
      st.Page(page='introducao/tabela.py', title="Tabela", icon=":material/house:"),
      st.Page(page='introducao/cubo.py', title="Cubo", icon=":material/help:"),
      st.Page(page='introducao/dashboard.py', title="Dashboard", icon=":material/help:"),
      st.Page(page='introducao/visualizacao.py', title="Vizualização", icon=":material/help:")
    ]
  }
)
pg.run()