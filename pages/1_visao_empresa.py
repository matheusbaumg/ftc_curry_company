#==============================
# importando bibliotecas
#==============================
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from haversine import haversine
import streamlit as st
from datetime import datetime
from PIL import Image
import folium
from streamlit_folium import folium_static
#----------------------------------------------------------------------------------

st.set_page_config(page_title='Visão Empresa', layout='wide')

#==============================
# Funções
#==============================

def country_maps(df1):
  ''' Fazer os comentários com o descritivo do que cada função faz 
  '''
  df_aux = df1.loc[:, ['Delivery_location_latitude', 'Delivery_location_longitude', 'City', 'Road_traffic_density']].groupby(['City', 'Road_traffic_density']).median().reset_index()
  # desenhando o mapa
  map = folium.Map(zoom_start=11)

  for index, location_info in df_aux.iterrows():
    folium.Marker([location_info['Delivery_location_latitude'],
                    location_info['Delivery_location_longitude']],
                    popup=location_info[['City', 'Road_traffic_density']]).add_to(map)

  folium_static(map, width=1024, height=600)
  return None


def order_share_by_week(df1):
  # será preciso fazer em dois passos
  # 1 - calcular a quantidade de pedidos por seman
  df_aux1 = df1.loc[:, ['ID', 'week_of_year']].groupby(['week_of_year']).count().reset_index()
  # 2 - calcular a quantidade de entregadores únicos por semana
  df_aux2 = df1.loc[:, ['Delivery_person_ID', 'week_of_year']].groupby(['week_of_year']).nunique().reset_index()
  # 3 - juntando od DataFrames criados
  df_aux = pd.merge(df_aux1, df_aux2, how='inner')
  df_aux.columns = ['semana', 'qnt_entregas', 'entregadores']
        # calculo da quantidade de pedidos por entregador a cada semana
  # qnt_entregas / entregadores
  df_aux['entrega_por_entregador'] = df_aux['qnt_entregas'] / df_aux['entregadores']
  # fazendo o gráfico de linha
  fig = px.line(df_aux, x='semana', y='entrega_por_entregador')

  return fig


def order_by_week(df1):
  # criando coluna das semanas
  df1['week_of_year'] = df1['Order_Date'].dt.strftime('%U')
  df_aux = df1.loc[:, ['ID', 'week_of_year']].groupby(['week_of_year']).count().reset_index()
  # renomeando as colunas
  df_aux.columns = ['week_of_year', 'qnt_entregas_semana']
  # criando o gráfico de barras
  fig = px.line(df_aux, x='week_of_year', y='qnt_entregas_semana')
  
  return fig


def traffic_order_city( df1 ):
  # seleção de linhas
  df_aux = df1.loc[:, ['ID', 'City', 'Road_traffic_density']].groupby(['City', 'Road_traffic_density']).count().reset_index()
  # mudando nome das colunas
  df_aux.columns = ['City', 'Road_traffic_density', 'qnt_entregas']
  # encontrando as % de cada situação
  df_aux['%_entregas'] = (df_aux['qnt_entregas']/(df_aux['qnt_entregas'].sum()))*100
  # criando o gráfico de bolhas
  fig = px.scatter(df_aux, x='City', y='Road_traffic_density', size='qnt_entregas', color='City')

  return fig


def traffic_order_share(df1):
  # seleção de linhas
  df_aux = df1.loc[:, ['ID', 'Road_traffic_density']].groupby(['Road_traffic_density']).count().reset_index()
  # trocando nomes das colunas
  df_aux.columns = ['condicao_trafego', 'qnt_entregas']
  # craindo a nova coluna
  df_aux['%_entregas'] = (df_aux['qnt_entregas'] / (df_aux['qnt_entregas'].sum()))*100
  # criando gráfico de pizza
  fig = px.pie(df_aux, values='%_entregas', names='condicao_trafego')

  return fig


def order_metrics( df1 ):
  # seleção de linhas
  df_aux = df1.loc[:, ['ID', 'Order_Date']].groupby(['Order_Date']).count().reset_index()
  # nomeando as colunas do DataFrame resultante para ficar melhor de interpretar o resultado
  df_aux.columns = ['order_date', 'qtd_entregas']
  # criando o gráfico de barras
  fig = px.bar(df_aux, x='order_date', y='qtd_entregas')
  # mostrando o gráfico
  
  return fig


# limpeza dos dados
def clean_code(df1):
  """ Esta função tem a responsabilidade de limpar o dataframe
  
      Tipos de limpeza:
      1. Remoção dos dados NaN
      2. Mudança do tipo da coluna de dados
      3. Remoção dos espaços das variáveis de texto
      4. Formatação coluna de datas
      5. Limpeza da colun ade tempo (remoção do texto da varoável numérica)

      Input: DataFrame
      Output: DataFrame

  """
  # 1 - removendo linhas com NaN
  linhas_selecionadas = (df1['Delivery_person_Age'] != 'NaN ')
  df1 = df1.loc[linhas_selecionadas, :].copy()

  linhas_selecionadas = (df1['multiple_deliveries'] != 'NaN ')
  df1 = df1.loc[linhas_selecionadas, :].copy()

  linhas_selecionadas = (df1['Road_traffic_density'] != 'NaN ')
  df1 = df1.loc[linhas_selecionadas, :].copy()

  linhas_selecionadas = (df1['City'] != 'NaN ')
  df1 = df1.loc[linhas_selecionadas, :].copy()

  linhas_selecionadas = (df1['Festival'] != 'NaN ')
  df1 = df1.loc[linhas_selecionadas, :].copy()


  # 2 - convertendo o tipo de texto para numero
  df1['Delivery_person_Age'] = df1['Delivery_person_Age'].astype(int)

  df1['multiple_deliveries'] = df1['multiple_deliveries'].astype(int)
  

  # 3 - convertendo a coluna Ratings de texto para numero decimal (float)
  df1['Delivery_person_Ratings'] = df1['Delivery_person_Ratings'].astype(float)
  

  # 4 - convertendo a coluna order_date de texto para data
  df1['Order_Date'] = pd.to_datetime(df1['Order_Date'], format='%d-%m-%Y')
  

  # 5 - removendo os espaços dentro de strings/texto/object
  df1.loc[:, 'ID'] = df1.loc[:, 'ID'].str.strip()
  df1.loc[:, 'Road_traffic_density'] = df1.loc[:, 'Road_traffic_density'].str.strip()
  df1.loc[:, 'Type_of_order'] = df1.loc[:, 'Type_of_order'].str.strip()
  df1.loc[:, 'Type_of_vehicle'] = df1.loc[:, 'Type_of_vehicle'].str.strip()
  df1.loc[:, 'City'] = df1.loc[:, 'City'].str.strip()
  df1.loc[:, 'Festival'] = df1.loc[:, 'Festival'].str.strip()
 

  # 6 - limpando a coluna de Time_taken
  df1['Time_taken(min)'] = df1['Time_taken(min)'].apply(lambda x: x.split('(min) ')[1])
  # transformando em numero interiro
  df1['Time_taken(min)'] = df1['Time_taken(min)'].astype(int)

  return df1

#----------------------------------------------------------------------------------
#------------------------- Início da Estrutura Lógica do código -------------------

# import dataset
df = pd.read_csv('train.csv')

# fazendo uma cópia do DataFrame
df1 = df.copy()

# Limpando os dados
df1 = clean_code(df1)

#----------------------------------------------------------------------------------

#========================
### Barra lateral
#========================

# para executar com o stremlit usar o comando -> streamlit run <arquivo>

st.header('Marketplace - Visão Cliente')

# logo
#image_path = 'logo_alvo.jpg'
image = Image.open('logo_alvo.jpg')
st.sidebar.image(image, width=120)

# cabeçalho
st.sidebar.markdown('# Cury Company')
st.sidebar.markdown('## Fastest Delivery in Town')
st.sidebar.markdown('''___''')

# slide de seleção de datas
st.sidebar.markdown('Selecione uma data limite')

date_slider = st.sidebar.slider(
    'Até qual valor?',
    value=datetime(2022, 4, 13),
    min_value=datetime(2022, 2, 11),
    max_value=datetime(2022, 4, 6),
    format='DD-MM-YYYY')

#st.header(date_slider)
st.sidebar.markdown('''___''')

# seleção do tráfego
traffic_options = st.sidebar.multiselect(
    'Quais as condições do trânsito',
    ['Low', 'Medium', 'High', 'Jam'],
    default=['Low', 'Medium', 'High', 'Jam'])
st.sidebar.markdown('''___''')


# rodapé
st.sidebar.markdown('Powered by Comunidade DS')
st.sidebar.markdown('By MMB')
#=================================================================================

#========================
### Colocando os filtros para funcionar
#========================

# slider de data
linhas_selecionadas = df1['Order_Date'] < date_slider
df1 = df1.loc[linhas_selecionadas, :]

# filtro de trânsito
linhas_selecionadas = df1['Road_traffic_density'].isin(traffic_options)
df1 = df1.loc[linhas_selecionadas, :]


#=================================================================================

#========================
### Layout Streamlit
#========================

# criação das abas (tabs)
tab1, tab2, tab3 = st.tabs(['Visão Gerencial', 'Visão Tática', 'Visão Geográfica'])

# criando conteúdo da tab1
with tab1:
    with st.container():
      # Order Metrics
      st.markdown('# Orders by Day')
      fig = order_metrics( df1 )
      st.plotly_chart(fig, use_container_width=True)

    #criando conteiner para as colunas
    with st.container():
      # criando 2 colunas para colocar 2 figuras
      col1, col2 = st.columns(2)

      # conteúdo coluna 1
      with col1:
        st.header('Traffic Order Share')
        fig = traffic_order_share (df1)
        # mostrando o gráfico
        st.plotly_chart(fig, use_container_width=True)
        
      # conteúdo coluna 2
      with col2:
        st.header('Traffic Order City')
        fig = traffic_order_city( df1 )
        # mostrando o gráfico
        st.plotly_chart(fig, use_container_width=True)


# criando conteúdo da tab2
with tab2:
    with st.container():
      st.markdown('# Order by Week')
      fig = order_by_week(df1)
      # mostrando o grafico
      st.plotly_chart(fig, use_container_width=True)


    with st.container():
      st.markdown('# Order Share by Week')
      fig = order_share_by_week(df1)
      # mostrando o grafico
      st.plotly_chart(fig, use_container_width=True)    


# criando conteúdo da tab3
with tab3:
    st.markdown('Country Maps')
    country_maps(df1)

    





#=================================================================================