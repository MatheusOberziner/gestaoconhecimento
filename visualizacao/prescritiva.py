import streamlit as st
import pandas as pd
from prophet import Prophet
import pyomo.environ as pyo
from pyomo.opt import SolverFactory
from streamlit_extras.metric_cards import style_metric_cards


style_metric_cards(
    border_left_color="#9AD8E1",
    background_color="#fff",
    border_size_px=1,
    border_color="#CCC",
    border_radius_px=5,
    box_shadow=True
)


if st.button('Calcular'):
    grupo = st.session_state['df'].groupby(
        ['Order Date Month', 'product_sub_category']
    )[st.session_state['medida']].sum().reset_index()
    projecao = pd.DataFrame()
    with st.status(
            'Executando Projeção',
            expanded=True
    ) as status:
        for sub in grupo['product_sub_category'].unique():
            st.write(sub)
            grupo_sub = grupo[grupo['product_sub_category'] == sub]
            for medida in st.session_state['medida']:
                grupo_medida = grupo_sub[['Order Date Month', medida]]
                grupo_medida.columns = ['ds', 'y']
                future = Prophet().fit(grupo_medida).make_future_dataframe(
                    periods=1,
                    freq='MS'
                )
                forecast = Prophet().fit(grupo_medida).predict(future)
                forecast = forecast.tail(1)[
                    [
                        'ds',
                        'yhat',
                        'yhat_lower',
                        'yhat_upper'
                    ]
                ]
                forecast['product_sub_category'] = sub
                forecast['medida'] = medida
                projecao = pd.concat(
                    [
                        projecao,
                        forecast
                    ]
                )
        status.update(
            label="Projeção Completa!",
            state="complete",
            expanded=False
        )
    projecao_pivot = projecao.pivot_table(
        index='product_sub_category',
        columns='medida',
        values='yhat',
        aggfunc='sum'
    ).reset_index()
    st.subheader('Valores Projetados')
    st.dataframe(
        projecao_pivot,
        use_container_width=True,
        hide_index=True,
        height=650
    )
    valor_total = projecao_pivot['sales'].sum() - projecao_pivot['profit'].sum()
    unidades = projecao_pivot['order_quantity'].sum() * 0.7
    cols = st.columns(5)
    cols[0].metric(
        'Valor Projetado para Compras',
        round(valor_total, 2)
    )
    cols[1].metric(
        'Valor Projetado para Unidades',
        round(unidades, 0)
    )

    indice = list(projecao_pivot.index.values)
    lucro = projecao_pivot['profit'].values
    quantidade = projecao_pivot['order_quantity'].values
    valor = projecao_pivot['sales'].values
    model = pyo.ConcreteModel()
    model.x = pyo.Var(indice, within=pyo.Binary)
    x = model.x
    model.valores_constraint = pyo.Constraint(
        expr=sum(
            [x[p] * valor[p] for p in indice]
        ) <= valor_total
    )
    model.quantidade_constraint = pyo.Constraint(
        expr=sum(
            [x[p] * quantidade[p] for p in indice]
        ) <= unidades)
    model.objective = pyo.Objective(
        expr=sum(
            [x[p] * lucro[p] for p in indice]
        ),
        sense=pyo.maximize
    )
    opt = SolverFactory(
        'glpk',
        executable='C:/Users/1023343/Desktop/gestaoconhecimento/visualizacao/w64/glpsol.exe'
    )
    results = opt.solve(model)
    solution = [int(pyo.value(model.x[p])) for p in indice]

    projecao_pivot['Comprar'] = solution
    cols[2].metric(
        'Valor Otimizado Compras',
        round(projecao_pivot[projecao_pivot['Comprar'] == 1]['sales'].sum(), 2)
    )
    cols[3].metric(
        'Quantidade Otimizada Compras',
        round(projecao_pivot[projecao_pivot['Comprar'] == 1]['order_quantity'].sum(), 0)
    )
    cols[4].metric(
        'Lucro Otimizado Compras',
        round(projecao_pivot[projecao_pivot['Comprar'] == 1]['profit'].sum(), 2)
    )
    st.subheader('Valores Otimizados')
    st.dataframe(
        projecao_pivot,
        use_container_width=True,
        hide_index=True,
        height=650
    )