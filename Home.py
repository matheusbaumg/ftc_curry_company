# bibliotecas
import streamlit as st
from PIL import Image

# confifuração da página
st.set_page_config(
    page_title='Home',
    page_icon=':material/home:',
    layout='centered'
                                )


# imagem (logo)
image = Image.open('logo_alvo.jpg')
st.sidebar.image(image, width=100)


# cabeçalho
st.sidebar.markdown('# Cury Company')
st.sidebar.markdown('## Fastest Delivery in Town')

st.sidebar.divider()

st.write('# Curry Company Growth Dashboard')

st.markdown(
    '''
    Growth Dashboard foi construido para acompanhar as métricas de crescimento das Entregadores e Restaurantes.
    
    ### Como utilizar esse Growth Dashboard?
    - Visão Empresa:
        - Visão Gerencial: Métricas gerais de acompanhamento.
        - Visão Tática: Indicadores semanais de crescimento.
        - Visão Geográfica: Insights de geolocallização.
    - Visão Entregador:
        - Acompanhamento dos indicadores semanais de crescimento.
    - Visão Restaurantes:
        - Indicadores semanais de crescimento dos restaurantes.
    
        ----------------------------------------------------

        ### Ask for Help
        - Contato no Discord
            - @matheusbaumg

''')
