import streamlit as st
from PIL import Image

st.set_page_config(
    page_title='Home',
    page_icon='🎲',
    layout='centered',
)


# imagem (logo)
#image_path = '/home/matheusmb/CDS/FTC/'
image = Image.open('logo_alvo.jpg')
st.sidebar.image(image, width=120)


# cabeçalho
st.sidebar.markdown('# Cury Company')
st.sidebar.markdown('## Fastest Delivery in Town')
st.sidebar.markdown('''___''')

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
        - Time de Data Science no Discord
            - @meigarom
            - @matheusbaumg

''')
