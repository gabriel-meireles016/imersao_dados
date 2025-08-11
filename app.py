import streamlit as st
import pandas as pd
import plotly.express as px
import pycountry as pcy

# ====== Configuração da Página ======
# Título, ícone e layout
st.set_page_config(
    page_title="Dashboard de Salários na Área de Dados",
    page_icon="📊",
    layout='wide'
)

# ====== Upload dos Dados ======
df = pd.read_csv("https://raw.githubusercontent.com/vqrca/dashboard_salarios_dados/refs/heads/main/dados-imersao-final.csv")

# Sidebar
st.sidebar.header("Filtros")

# ====== Filtragem dos Dados ======
# FILTRO -> Ano
anos_disponiveis = sorted(df['ano'].unique())
anos_selecionados = st.sidebar.multiselect("Ano", anos_disponiveis)

# FILTRO -> Nível de Experiência
xp_disponiveis = sorted(df['senioridade'].unique())
xp_selecionados = st.sidebar.multiselect("Nível de Experiência", xp_disponiveis)

# FILTRO -> Contrato
contrato_disponiveis = sorted(df['contrato'].unique())
contrato_selecionados = st.sidebar.multiselect("Contrato", contrato_disponiveis)

# FILTRO -> Tamanho da Empresa
tamanho_disponiveis = sorted(df['tamanho_empresa'].unique())
tamanho_selecionados = st.sidebar.multiselect("Tamanho da Empresa", tamanho_disponiveis)

# SELEÇÕES
df_filtrado = df[
    (df['ano'].isin(anos_selecionados)) &
    (df['senioridade'].isin(xp_selecionados)) &
    (df['contrato'].isin(contrato_selecionados)) &
    (df['tamanho_empresa'].isin(tamanho_selecionados))
]

# ====== Parte Principal ======
st.title("Dashboard de Análise de Salários na Área de Dados")
st.markdown("Analise as informações salariais dos últimos anos na Área de Dados. Use o filtro a esquerda para melhorar sua busca.")

# ====== Métricas principais ======
st.subheader("Métricas Gerais (Salário Anual USD)")

if not df_filtrado.empty:
    salario_medio = df_filtrado['usd'].mean()
    salario_maximo = df_filtrado['usd'].max()
    salario_minimo = df_filtrado['usd'].min()
    total_registros = df_filtrado.shape[0]
    cargo_mais_frequente = df_filtrado['cargo'].mode()[0]
else:
    salario_medio, salario_maximo, salario_minimo, total_registros, cargo_mais_frequente = 0, 0, 0, 0, ""

col1, col2, col3, col4, col5 = st.columns(5)
col1.metric("Salário Médio", f"USD {salario_medio:.2f}")
col2.metric("Salário Máximo", f"USD {salario_maximo:.2f}")
col3.metric("Salário Mínimo", f"USD {salario_minimo:.2f}")
col4.metric("Total de Registros", total_registros)
col5.metric("Cargo mais Frequente", cargo_mais_frequente)

st.markdown("---")

# ====== Gráficos com Plotly ======
st.subheader("Gráficos")

col_graf1, col_graf2 = st.columns(2)

with col_graf1:
    if not df_filtrado.empty:
        melhores_cargos = df_filtrado.groupby('cargo')['usd'].mean().nlargest(10).round(2).sort_values(ascending=True).reset_index() # nlargest(10) -> 10 primeiros

        grafico_cargos = px.bar(
            melhores_cargos,
            x='usd',
            y='cargo',
            #orientation='h',
            title="Os 10 melhores cargos por salário médio",
            labels={
                'usd': 'Média Salarial Anual (USD)',
                'cargo': ''
            }
        )

        #grafico_cargos.update_layout(title_x=0.1, yaxis={'categoryorder':'total ascending'})        
        st.plotly_chart(grafico_cargos, use_container_width=True)
    else:
        st.warning("Nenhum dado a ser exibido no gráfico de cargos.")

with col_graf2:
    if not df_filtrado.empty:
        histograma_cargos = px.histogram(
            df_filtrado,
            x='usd',
            nbins=30,
            title="Distribuição de Salários Anuais",
            labels={
                'usd': 'Faixa Salarial',
                'count': ''
            }
        )

        histograma_cargos.update_layout(title_x=0.1)
        st.plotly_chart(histograma_cargos, use_container_width=True)
    else:
        st.warning("Nenhum dado a ser exibido no gráfico de cargos.")

st.markdown("---")

col_graf3, col_graf4 = st.columns(2)

with col_graf3:
    if not df_filtrado.empty:
        remoto_contagem = df_filtrado['remoto'].value_counts().reset_index()
        remoto_contagem.columns = ['tipo_trabalho', 'quantidade']
        
        grafico_remoto = px.pie(
            remoto_contagem,
            names='tipo_trabalho',
            values='quantidade',
            title='Proporção dos Tipos de Trabalho',
            hole=0.5
        )

        grafico_remoto.update_traces(textinfo='percent+label')
        grafico_remoto.update_layout(title_x=0.1)
        st.plotly_chart(grafico_remoto, use_container_width=True)
    else:
        st.warning("Nenhum dado a ser exibido no gráfico de cargos.")

with col_graf4:
    if not df_filtrado.empty:
        media_ds_pais = df_filtrado[df_filtrado['cargo'] == 'Data Scientist'].groupby('residencia_iso3')['usd'].mean().round(2).reset_index()
        
        mapa_salarial = px.choropleth(
            media_ds_pais,
            locations='residencia_iso3',
            color='usd',
            color_continuous_scale='rdylgn',
            title='Salário Médio de Cientista de Dados por País',
            labels={
                'usd': 'Salário Médio (USD)',
                'residencia_iso3': 'País'
            }
        )

        mapa_salarial.update_layout(title_x=0.1)
        st.plotly_chart(mapa_salarial, use_container_width=True)
    else:
        st.warning("Nenhum dado a ser exibido no gráfico de cargos.")

st.markdown('---')

st.subheader("Dados Detalhados")
st.dataframe(df_filtrado)