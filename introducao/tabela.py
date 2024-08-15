import streamlit as st

st.title('Tabela')
st.dataframe(
  st.session_state['df'],
  hide_index=True,
  use_container_width=True,
  column_config={
    'order_date': st.column_config.DateColumn(label='Data do Pedido'),
    'ship_date': st.column_config.DateColumn(label='Data de Envio'),
    'profit': st.column_config.NumberColumn(label='Lucro', format='R$ %.2f')
  }
)