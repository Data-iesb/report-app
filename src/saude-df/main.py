import streamlit as st
import pandas as pd
import numpy as np

# ✅ No set_page_config here

# Header
st.title("📊 Relatório de Saúde Pública - Distrito Federal")
st.markdown("""
Este relatório apresenta dados fictícios de hospitais no Distrito Federal,
utilizados apenas para fins de teste da plataforma de relatórios Streamlit.
""")

# Summary metrics
col1, col2, col3 = st.columns(3)
col1.metric("Pacientes Atendidos", "1.284", "+8%")
col2.metric("Recuperações", "1.012", "+5%")
col3.metric("Taxa de Ocupação", "72%", "-2%")

# Generate sample data
df = pd.DataFrame({
    "Hospital": ["Hospital A", "Hospital B", "Hospital C", "Hospital D"],
    "Pacientes": np.random.randint(300, 800, size=4),
    "Recuperados": np.random.randint(200, 700, size=4),
})

# Table
st.markdown("### 🏥 Dados por Hospital")
st.dataframe(df)

# Chart
st.markdown("### 📈 Comparativo de Pacientes e Recuperados")
st.bar_chart(df.set_index("Hospital")[["Pacientes", "Recuperados"]])

# Footer
st.markdown("---")
st.caption("© IESB • Simulação de Relatório para Fins de Teste • 2025")

