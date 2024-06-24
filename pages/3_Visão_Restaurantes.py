#===============================
# Bibliotecas
#===============================
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from haversine import haversine
import streamlit as st
from datetime import datetime
from PIL import Image
import numpy as np
#----------------------------------------------------------------------------------

# Configuração da página
st.set_page_config(page_title='Visão Restaurantes', layout='wide')

#==============================
# Funções
#==============================

def avg_std_time_on_traffic(df1):
    ''' Esta função tem como objetivo a construção de um gráfico tipo Sunburstque apresenta o tempo médio e o desvio padrão do tempo de entrega por cidade e por condição de tráfego.

        Input: DataFrame
        Output: Gráfico do tipo Sunburst
    '''
    df_aux = df1.loc[:, ['Time_taken(min)', 'City', 'Road_traffic_density']].groupby(['City', 'Road_traffic_density']).agg({'Time_taken(min)': ['mean', 'std']})
    df_aux.columns = ['avg_time', 'std_time']
    df_aux = df_aux.reset_index()

    fig = px.sunburst(df_aux,
                      path=['City', 'Road_traffic_density'], 
                      values='avg_time', color='std_time', 
                      color_continuous_scale='Bluered', 
                      color_continuous_midpoint= np.average(df_aux['std_time']),
                      labels={'avg_time':'Tempo Médio', 'std_time':'Desvio Padrão'})

    return fig


def avg_std_time_graph(df1):
    ''' Esta função tem como objetivo a construção de um gráfico de barras com indicadores de desvio padrão que mostre os dados do tempo médio das entregas por cidade.

        Input: DataFrame
        Output: Gráfico de barras com indicadores de desvio padrão
    '''

    df_aux = df1.loc[:, ['Time_taken(min)', 'City']].groupby(['City']).agg({'Time_taken(min)': ['mean', 'std']})
    df_aux.columns = ['avg_time', 'std_time']
    df_aux = df_aux.reset_index()
    fig = go.Figure()
    fig.add_trace(go.Bar(name='Control', x=df_aux['City'], y=df_aux['avg_time'], error_y=dict(type='data', array=df_aux['std_time'])))
    fig.update_layout(barmode='group')

    return fig


def distance(df1):
    ''' Esta função tem como objetivo o cálculo da distância média entre a localização do restaurante e do local da entrega

        Input: DataFrame
        Output: DataFrame
    '''
    colunas = ['Restaurant_latitude', 'Restaurant_longitude', 'Delivery_location_latitude', 'Delivery_location_longitude']
    df1['distance'] = df1.loc[:, colunas].apply( lambda x: haversine((x['Restaurant_latitude'], x['Restaurant_longitude']), (x['Delivery_location_latitude'], x['Delivery_location_longitude'])), axis=1)
    avg_distance = np.round(df1['distance'].mean(), 2)

    return avg_distance


def avg_std_time_delivery(df1, festival, op):
    ''' Esta função calcula o tempo médio e o desvio padão do tempo de entrega.

        Parâmetros:
            Input:
                - df: DataFrame com os dados necessários para o cálculo
                - op: Tipo de operação que precisa ser calculado
                        'avg_time': Calcula o tempo médio
                        'std_time': Calcula o desvio padrão do tempo
            Output:
                - df: DataFrame com 2 colunas e 1 linha.
    '''
    df_aux = df1.loc[:, ['Time_taken(min)','Festival']].groupby(['Festival']).agg({'Time_taken(min)': ['mean', 'std']})
    df_aux.columns = ['avg_time', 'std_time']
    df_aux = df_aux.reset_index()
    df_aux = np.round(df_aux.loc[df_aux['Festival'] == festival, op],2)

    return df_aux


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

#==================================================================================

#------------------------- Início da Estrutura Lógica do código -------------------

# import dataset
df = pd.read_csv('train.csv')

# fazer uma copia de df para df1
df1 = df.copy()

# limpeza do dataframe
df1 = clean_code(df1)

#----------------------------------------------------------------------------------

#===============================
#Barra lateral
#===============================

# Cabeçalho da página
st.header('Marketplace - Visão Restaurantes')

# logo
image = Image.open('logo_alvo.jpg')
st.sidebar.image(image, width=120)

# cabeçalho
st.sidebar.markdown('# Cury Company')
st.sidebar.markdown('## Fastest Delivery in Town')
st.sidebar.divider()

# slide de seleção de datas
st.sidebar.markdown('Selecione uma data limite')

date_slider = st.sidebar.slider(
    'Até qual valor?',
    value=datetime(2022, 4, 6),
    min_value=datetime(2022, 2, 11),
    max_value=datetime(2022, 4, 6),
    format='DD-MM-YYYY')

st.sidebar.divider()

# seleção do tráfego
traffic_options = st.sidebar.multiselect(
    'Quais as condições do trânsito',
    ['Low', 'Medium', 'High', 'Jam'],
    default=['Low', 'Medium', 'High', 'Jam'])
st.sidebar.divider()


# rodapé
st.sidebar.markdown('Desenvolvido por:')
st.sidebar.markdown('Matheus Maranho Baumguertner')
#=================================================================================

#===============================
# Filtros
#===============================

# slider de data
linhas_selecionadas = df1['Order_Date'] < date_slider
df1 = df1.loc[linhas_selecionadas, :]

# filtro de trânsito
linhas_selecionadas = df1['Road_traffic_density'].isin(traffic_options)
df1 = df1.loc[linhas_selecionadas, :]

#----------------------------------------------------------------------------------

#===============================
# Layout Streamlit
#===============================


# linha 1
with st.container():
    st.title('Overall Metrics')

    col1, col2, col3 = st.columns(3)

    col1 = col1.container()
    with col1:
        delivery_unique = len(df1.loc[:, 'Delivery_person_ID'].unique())
        col1.metric('Entregadores únicos', delivery_unique)

        avg_distance = distance(df1)
        col1.metric('Distancia média das entregas (Km)', avg_distance)


    col2 = col2.container()
    with col2:
        df_aux = avg_std_time_delivery(df1, 'Yes', 'avg_time')
        col2.metric('Tempo médio de entrega com Festival (min)', df_aux)

        df_aux = avg_std_time_delivery(df1, 'Yes', 'std_time')
        col2.metric('Desvio parão do tempo de entrega com Festival', df_aux)


    col3 = col3.container()
    with col3:
        df_aux = avg_std_time_delivery(df1, 'No', 'avg_time')
        col3.metric('Tempo médio de entrega sem Festival (min)', df_aux)


        df_aux = avg_std_time_delivery(df1, 'No', 'std_time')
        col3.metric('Desvio parão do tempo de entrega sem Festival', df_aux)

st.divider()

# linha 2
with st.container():

    col1, col2 = st.columns(2)

    # linha 2, coluna 1
    with col1:
        st.header('Tempo médio de entrega por cidade')
        fig = avg_std_time_graph(df1)
        st.plotly_chart(fig, use_container_width=True)

    # linha 2, coluna 2
    with col2:
        st.header('Distribuição da distância')
        df_aux = df1.loc[:, ['Time_taken(min)', 'City', 'Type_of_order']].groupby(['City', 'Type_of_order']).agg({'Time_taken(min)': ['mean', 'std']})
        df_aux.columns = ['avg_time', 'std_time']
        df_aux = df_aux.reset_index()
        st.dataframe(df_aux, use_container_width=True, column_config={'Type_of_order': st.column_config.Column('Tipo de pedido', width='small'), 'avg_time': st.column_config.NumberColumn('Tempo médio (min)', width='small'), 'std_time':'Desvio padrão'}, hide_index=True, height=455)

st.divider()

# linha 3
with st.container():
    
    col1, col2 = st.columns(2)
    
    # linha 3, coluna 1
    with col1:
        st.subheader('Distribuição da distância média das entregas por cidade')
        colunas = ['Restaurant_latitude', 'Restaurant_longitude', 'Delivery_location_latitude', 'Delivery_location_longitude']
        df1['distance'] = df1.loc[:, colunas].apply( lambda x: haversine((x['Restaurant_latitude'], x['Restaurant_longitude']), (x['Delivery_location_latitude'], x['Delivery_location_longitude'])), axis=1)
    
        avg_distance = df1.loc[:, ['City', 'distance']].groupby('City').mean().reset_index()
    
        fig = go.Figure(data=[go.Pie(labels=avg_distance['City'], values=avg_distance['distance'], pull=[0, 0.1, 0] )])
        # usa o pull pra 'puxar'um pedaço da pizza, mudando os valores muda o pedaço puxado e a distacia que fica da pizza
        st.plotly_chart(fig)
        

    # linha 3, coluna 2
    with col2:
        st.subheader('Tempo médio e desvio padrão de entrega por cidade e condição de tráfego')
        fig = avg_std_time_on_traffic(df1)
        st.plotly_chart(fig)

#=================================================================================      