import streamlit as st
import pandas as pd
from prophet import Prophet
from sklearn.ensemble import RandomForestRegressor
import random


tabs = st.tabs(['Projeção de Valores', 'Previsão de Valor'])
with tabs[0]:
    medida = st.selectbox('Medidas para Predição', st.session_state['medida'])
    if st.toggle('Calcular Previsão'):
        projecao = st.session_state['df'].groupby('Order Date Month')[[medida]].sum().reset_index()
        projecao.columns=['ds', 'y']
        future = Prophet().fit(projecao).make_future_dataframe(periods=12, freq='MS')
        forecast = Prophet().fit(projecao).predict(future)
        cols = st.columns(2)
        cols[0].pyplot(Prophet().fit(projecao).plot(forecast))
        cols[1].dataframe(
            forecast.tail(12)[
                [
                    'ds', 'yhat', 'yhat_lower', 'yhat_upper'
                ]
            ],
            hide_index=True,
            use_container_width=True,
            height=480
        )
with tabs[1]:
    medida = st.selectbox('Selecione a Medida', st.session_state['medida'])
    dimensao = st.multiselect('Selecione a dimensão: ', st.session_state['dimensao'] + st.session_state['dimensao_tempo'])
    if len(dimensao) > 0:
        if st.toggle('Calcular'):
            regressao = st.session_state['df'][[medida] + dimensao]
            dummies = pd.get_dummies(st.session_state['df'][dimensao])
            rf = RandomForestRegressor(n_estimators=1000, random_state=42)
            rf.fit(dummies, st.session_state['df'][medida])
            amostra = dummies[
                dummies.index.isin(
                    random.sample(
                        range(0, len(dummies.index)),
                        k=10
                    )
                )
            ]
            previsao = rf.predict(amostra)
            amostra['previsao'] = previsao
            tabs = st.tabs(['DataFrame', 'Dummies', 'Amostra'])
            with tabs[0]:
                st.dataframe(regressao, use_container_width=True)
            with tabs[1]:
                st.dataframe(dummies, use_container_width=True)
            with tabs[2]:
                st.dataframe(amostra, use_container_width=True)