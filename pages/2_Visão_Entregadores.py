#===============================
# Bibliotecas
#===============================
import pandas as pd
import streamlit as st
from datetime import datetime
from PIL import Image
#----------------------------------------------------------------------------------

# Configuração da página
st.set_page_config(page_title='Visão Entregadores', layout='wide')

#==============================
# Funções
#==============================


def top_delivers(df1, top_asc):
    ''' Esta função tem como obejtivo encontrar os entregadores mais rápidos e os mais lentos

        Parâmetros:
            Input: 
                - df1: DataFrame com is dados necessários para o cálculo
                - top_asc: True ou False para a ordenação em ordem ascendente, crescente
                            - True: retorna os mais rápidos, com menores tempo
                            - False: retorna os mais lentos, com maiores tempos               
            Output: DataFrame
    '''
    df2 = (df1.loc[:, ['Time_taken(min)', 'City', 'Delivery_person_ID']]
        .groupby(['City', 'Delivery_person_ID'])
        .max()
        .sort_values(['City', 'Time_taken(min)'], ascending= top_asc).reset_index())
    
    df_aux1 = df2.loc[ df2['City'] == 'Metropolitian', :].head(10)
    df_aux2 = df2.loc[ df2['City'] == 'Urban', :].head(10)
    df_aux3 = df2.loc[ df2['City'] == 'Semi-Urban', :].head(10)
    df3 = pd.concat([df_aux1, df_aux2,df_aux3]).reset_index(drop=True)

    return df3


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
# Barra lateral
#===============================

# Cabeçalho da página
st.header('Marketplace - Visão Entregadores')

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

#=================================================================================

#===============================
# Layout Streamlit
#===============================

# linha 1
with st.container():
    st.title('Overall Metrics')

# linha 2
with st.container():

    col1, col2 = st.columns(2)
    
    # linha 2, coluna 1
    col1 = col1.container()
    with col1:
        st.subheader('Idade dos Entregadores')
        col3, col4 = st.columns(2)

        with col3:
            # maior idade
            maior_idade = df1.loc[:, 'Delivery_person_Age'].max()
            col3.metric('Maior idade', maior_idade)
        
        with col4:
            # menor idade
            menor_idade = df1.loc[:, 'Delivery_person_Age'].min()
            col4.metric('Menor idade', menor_idade)

    # linha 2, coluna 2
    col2 = col2.container()
    with col2:
        st.subheader('Condição dos veículos')
        col5, col6 = st.columns(2)
        
        with col5:
            # melhor condição 
            melhor_consicao = df1.loc[:, 'Vehicle_condition'].max()
            col5.metric('Melhor condição', melhor_consicao)
            
        with col6:
            # pior condição
            pior_condicao = df1.loc[:, 'Vehicle_condition'].min()
            col6.metric('Pior condição', pior_condicao)

st.divider()

# linha 3
with st.container():
    st.title('Avaliações')

    # criando colunas na linha 2
    col1, col2 = st.columns(2)

     # linha 3, coluna 1
    with col1:
        st.markdown('##### Avaliação média por entregador')
        df_aux = df1.loc[:, ['Delivery_person_Ratings', 'Delivery_person_ID']].groupby(['Delivery_person_ID']).mean().round(2).reset_index()
        # exibindo o dataframe
        st.dataframe(df_aux, column_config={'Delivery_person_ID': 'ID do entregador', 'Delivery_person_Ratings':'Avaliação média'}, use_container_width=True, height=525)

    # linha 3, coluna 2
    with col2:
        st.markdown('##### Avaliação média e desvio padrão por condição de tráfego')
        df_alt = df1.loc[:, ['Delivery_person_Ratings', 'Road_traffic_density']].groupby(['Road_traffic_density']).agg({'Delivery_person_Ratings': ['mean', 'std']})
        # renomeando as colunas
        df_alt.columns = ['delivery_mean', 'delivery_std']
        # reset do index
        df_alt = df_alt.reset_index()
        # exibindo o dataframe
        st.dataframe(df_alt, column_config={'Road_traffic_density':'Condição de tráfego', 'delivery_mean': 'Avaliação Média', 'delivery_std':'Devio padrão'}, use_container_width=True)


        st.markdown('##### Avaliação média e desvio padrão por condição climática')
        df_aux = df1.loc[:, ['Delivery_person_Ratings', 'Weatherconditions']].groupby(['Weatherconditions']).agg({'Delivery_person_Ratings': ['mean', 'std']})
        # renomeando as colunas
        df_aux.columns = ['delivery_mean', 'delivery_std']
        # reset do index
        df_aux = df_aux.reset_index()
        # exibindo o dataframe
        st.dataframe(df_aux, column_config={'Weatherconditions':'Condição Climática', 'delivery_mean':'Avaliação Média', 'delivery_std':'Desvio Padrão'}, use_container_width=True)

st.divider()

# linha 4
with st.container():
    st.title('Velocidade de entrega')
    
    # criando colunas da linha 4
    col1, col2 = st.columns(2)

    # linha 4, colun 1
    with col1:
        st.markdown('##### Entregadores mais rápidos')
        df3 = top_delivers(df1, top_asc=True)
        st.dataframe(df3, column_config={'Delivery_person_ID':'ID do entregador', 'Time_taken(min)':'Tempo (min)'}, use_container_width=True)

    # linha 4, coluna 2
    with col2:
        st.markdown('##### Entregadores mais lentos')
        df3 = top_delivers(df1, top_asc=False)
        st.dataframe(df3, column_config={'Delivery_person_ID':'ID do entregador', 'Time_taken(min)':'Tempo (min)'}, use_container_width=True)

#=================================================================================