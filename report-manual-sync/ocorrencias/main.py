import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.io as pio

st.markdown(f'<link href=""https://dataiesb-site.s3.sa-east-1.amazonaws.com/style.css" rel="stylesheet">', unsafe_allow_html=True)


# ✅ Bootstrap-compatible color palette
custom_colors = [
    "#dc3545",  # bright red (anchor)
    "#a32531",  # deeper red
    "#6e151e",  # dark wine
    "#260305",  # almost black-red
]



# ✅ Optional: Set global plotly theme
pio.templates.default = "plotly_white"


def main():
    # Example data (replace with your actual dataframe)
    # Assuming `ocorrencia_filtrada`, `meses_selecionados`, and `pagina` are already defined
    # For demo purposes, we'll simulate them below (REMOVE this when using real inputs):

    # Sample setup (mock data)
    # You should replace this with your real data loading and filtering logic
    ocorrencia_filtrada = pd.DataFrame({
        'mes': [1, 1, 2, 2],
        'ano': [2023, 2023, 2024, 2024],
        'feminino': [10, 20, 15, 25],
        'masculino': [15, 25, 20, 30],
        'total_vitimas': [25, 45, 35, 55]
    })

    meses_selecionados = [1, 2]  # Example filter
    pagina = st.selectbox("Escolha a página:", ["Gráficos", "Tabela de Ocorrências"])

    # Apply month filter
    ocorrencia_filtrada = ocorrencia_filtrada[ocorrencia_filtrada["mes"].isin(meses_selecionados)]

    if pagina == "Gráficos":
        st.title("Análise Gráfica das Ocorrências Criminais")

        col1, col2 = st.columns(2)

        # Donut Chart: Distribuição de Gênero
        genero_distribuicao = ocorrencia_filtrada[['feminino', 'masculino']].sum().reset_index()
        genero_distribuicao.columns = ['Genero', 'Total']

        fig_donut = px.pie(
            genero_distribuicao,
            names='Genero',
            values='Total',
            hole=0.4,
            title="Distribuição de Gênero por Ocorrência",
            color_discrete_sequence=custom_colors
        )
        fig_donut.update_traces(textinfo='percent+label')
        col1.plotly_chart(fig_donut, use_container_width=True)

        # Bar Chart: Total de Vítimas por Gênero por Ano
        vitimas_por_ano = ocorrencia_filtrada.groupby('ano')[['feminino', 'masculino']].sum().reset_index()

        fig_colunas = px.bar(
            vitimas_por_ano,
            x='ano',
            y=['feminino', 'masculino'],
            title="Total de Vítimas por Gênero por Ano",
            labels={'value': 'Total de Vítimas', 'variable': 'Gênero'},
            barmode='group',
            color_discrete_sequence=custom_colors[:2]
        )
        col2.plotly_chart(fig_colunas, use_container_width=True)

        # Line Chart: Quantidade de Vítimas ao Longo do Tempo
        st.subheader("Quantidade de Vítimas ao Longo do Tempo")
        vitimas_tempo = ocorrencia_filtrada.groupby(['ano', 'mes'])['total_vitimas'].sum().reset_index()

        vitimas_tempo['data'] = pd.to_datetime(
            vitimas_tempo['ano'].astype(str) + '-' + vitimas_tempo['mes'].astype(str).str.zfill(2) + '-01'
        )

        fig_linha = px.line(
            vitimas_tempo,
            x='data',
            y='total_vitimas',
            title="Quantidade de Vítimas ao Longo do Tempo",
            labels={'data': 'Data', 'total_vitimas': 'Quantidade de Vítimas'},
            markers=True,
            color_discrete_sequence=[custom_colors[2]]
        )
        st.plotly_chart(fig_linha, use_container_width=True)

    elif pagina == "Tabela de Ocorrências":
        st.title("Tabela de Ocorrências Criminais Filtradas")
        st.dataframe(ocorrencia_filtrada)

if __name__ == "__main__":
    main()

