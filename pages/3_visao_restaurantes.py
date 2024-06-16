#===============================
### importando bibliotecas
#===============================
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from haversine import haversine
import streamlit as st
from datetime import datetime
from PIL import Image
import folium
from streamlit_folium import folium_static
import numpy as np
import plotly.graph_objects as go
#----------------------------------------------------------------------------------

st.set_page_config(page_title='Visão Restaurantes', layout='wide')

#==============================
# Funções
#==============================

def avg_std_time_on_traffic(df1):
    df_aux = df1.loc[:, ['Time_taken(min)', 'City', 'Road_traffic_density']].groupby(['City', 'Road_traffic_density']).agg({'Time_taken(min)': ['mean', 'std']})
    df_aux.columns = ['avg_time', 'std_time']
    df_aux = df_aux.reset_index()

    fig = px.sunburst(df_aux, path=['City', 'Road_traffic_density'], values='avg_time', color='std_time', color_continuous_scale='RdBu', color_continuous_midpoint= np.average(df_aux['std_time']))

    return fig


def avg_std_time_graph(df1):

    df_aux = df1.loc[:, ['Time_taken(min)', 'City']].groupby(['City']).agg({'Time_taken(min)': ['mean', 'std']})
    df_aux.columns = ['avg_time', 'std_time']
    df_aux = df_aux.reset_index()
    fig = go.Figure()
    fig.add_trace(go.Bar(name='Control', x=df_aux['City'], y=df_aux['avg_time'], error_y=dict(type='data', array=df_aux['std_time'])))
    fig.update_layout(barmode='group')

    return fig


def distance(df1):
    colunas = ['Restaurant_latitude', 'Restaurant_longitude', 'Delivery_location_latitude', 'Delivery_location_longitude']
    df1['distance'] = df1.loc[:, colunas].apply( lambda x: haversine((x['Restaurant_latitude'], x['Restaurant_longitude']), (x['Delivery_location_latitude'], x['Delivery_location_longitude'])), axis=1)
    avg_distance = np.round(df1['distance'].mean(), 2)

    return avg_distance


def avg_std_time_delivery(df1, festival, op):
    '''
        Esta função calcula o tempo médio e o desvio padão do tempo de entrega.

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

#----------------------------------------------------------------------------------

# import dataset
df = pd.read_csv('train.csv')

# fazer uma copia de df para df1
df1 = df.copy()

# limpeza do dataframe
df1 = clean_code(df1)

#----------------------------------------------------------------------------------

#===============================
### Barra lateral
#===============================
# para executar com o stremlit usar o comando -> streamlit run <arquivo>

st.header('Marketplace - Visão Restaurantes')

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
st.sidebar.markdown('By Matheus Maranho Baumguertner')
#----------------------------------------------------------------------------------

#===============================
### Colocando os filtros para funcionar
#===============================

# slider de data
linhas_selecionadas = df1['Order_Date'] < date_slider
df1 = df1.loc[linhas_selecionadas, :]

# filtro de trânsito
linhas_selecionadas = df1['Road_traffic_density'].isin(traffic_options)
df1 = df1.loc[linhas_selecionadas, :]

#----------------------------------------------------------------------------------

#===============================
### Layout Streamlit
#===============================

# criando as abas
tab1, tab2, tab3 = st.tabs(['Visão Gerencial', '_', '_'])

# aba 1
with tab1:
    # linha 1
    with st.container():
        st.title('Overall Metrics')
        # criando as colunas da linha 1
        col1, col2, col3, col4, col5, col6 = st.columns(6)

        # linha 1, coluna 1
        with col1:
            #st.markdown('##### coluna 1')
            delivery_unique = len(df1.loc[:, 'Delivery_person_ID'].unique())
            col1.metric('Entregadores únicos', delivery_unique)
        
        # linha 1, coluna 2
        with col2:
            #st.markdown('##### coluna 2')
            avg_distance = distance(df1)
            col2.metric('A distancia média das entregas', avg_distance)

        # linha 1, coluna 3
        with col3:
            #st.markdown('##### coluna 3')    
            df_aux = avg_std_time_delivery(df1, 'Yes', 'avg_time')
            col3.metric('Tempo médio de entrega com Festival', df_aux)
            
        # linha 1, coluna 4
        with col4:
            #st.markdown('##### coluna 4')
            df_aux = avg_std_time_delivery(df1, 'Yes', 'std_time')
            col4.metric('STD tempo de entrega com Festival', df_aux)

        # linha 2, coluna 5
        with col5:
            #st.markdown('##### coluna 5')
            df_aux = avg_std_time_delivery(df1, 'No', 'avg_time')
            col5.metric('Tempo médio de entrega sem Festival', df_aux)

        # linha 1, coluna 6
        with col6:
            #st.markdown('##### coluna 6')
            df_aux = avg_std_time_delivery(df1, 'No', 'std_time')
            col6.metric('STD tempo de entrega sem Festival', df_aux)
            
    # linha 2
    with st.container():
        st.markdown('''___''')

        col1, col2 = st.columns(2)

        # linha 2, coluna 1
        with col1:
            # gráfico de barras com desvios padrão
            st.title('Tempo médio de entrega por cidade')
            fig = avg_std_time_graph(df1)
            st.plotly_chart(fig)

        # linha 2, coluna 2
        with col2:
            st.title('Distribuição da distância')
            df_aux = df1.loc[:, ['Time_taken(min)', 'City', 'Type_of_order']].groupby(['City', 'Type_of_order']).agg({'Time_taken(min)': ['mean', 'std']})
            df_aux.columns = ['avg_time', 'std_time']
            df_aux = df_aux.reset_index()
            st.dataframe(df_aux)

        

    # linha 3
    with st.container():
        st.markdown('''___''')
        st.title('Distribuição do tempo')

        col1, col2 = st.columns(2)
        
        # linha 3, coluna 1
        with col1:
            #st.markdown('##### coluna 1')
            # pizza tempos
            
            colunas = ['Restaurant_latitude', 'Restaurant_longitude', 'Delivery_location_latitude', 'Delivery_location_longitude']
            df1['distance'] = df1.loc[:, colunas].apply( lambda x: haversine((x['Restaurant_latitude'], x['Restaurant_longitude']), (x['Delivery_location_latitude'], x['Delivery_location_longitude'])), axis=1)
        
            avg_distance = df1.loc[:, ['City', 'distance']].groupby('City').mean().reset_index()
        
            fig = go.Figure(data=[go.Pie(labels=avg_distance['City'], values=avg_distance['distance'], pull=[0, 0.1, 0])])
            # usa o pull pra 'puxar'um pedaço da pizza, mudando os valores muda o pedaço puxado e a distacia que fica da pizza
            st.plotly_chart(fig)
            

        # linha 3, coluna 2
        with col2:
            #st.markdown('##### coluna 2')
            fig = avg_std_time_on_traffic(df1)
            st.plotly_chart(fig)      