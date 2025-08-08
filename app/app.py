import streamlit as st
import pandas as pd
import boto3
import json

S3_BUCKET = "dataiesb"
s3_client = boto3.client('s3')

def load_reports_json():
    """Fetch reports.json from S3"""
    try:
        # Load the reports.json from S3
        response = s3_client.get_object(Bucket=S3_BUCKET, Key="reports.json")
        reports_json = json.loads(response["Body"].read())
        return reports_json
    except Exception as e:
        st.error(f"❌ Erro ao carregar o arquivo 'reports.json': {e}")
        return {}

def list_reports_in_s3(reports_json):
    """List reports from the loaded JSON data"""
    return [report_id for report_id in reports_json if not reports_json[report_id]["deletado"]]

def load_and_execute_report(report_id, reports_json):
    """Download and execute the main.py script from S3"""
    try:
        # Look up the report by its ID in the JSON data
        report = reports_json.get(str(report_id))
        if not report:
            st.error(f"❌ Relatório não encontrado para o ID: {report_id}")
            return
        
        # Get the S3 path for the main.py script
        s3_key = f"{report['id_s3']}main.py"
        with tempfile.NamedTemporaryFile(mode="wb", suffix=".py", delete=False) as tmp:
            s3_client.download_fileobj(S3_BUCKET, s3_key, tmp)
            tmp_path = tmp.name

        with open(tmp_path, "r") as f:
            code = f.read()
        exec(code, {"__name__": "__main__"})
    except Exception as e:
        st.error(f"❌ Erro ao carregar o relatório '{report_id}': {e}")

def show_homepage(reports_json):
    st.title("Central de Relatórios Dinâmicos 📊")
    st.markdown("Escolha um relatório abaixo.")
    
    # Convert the reports_json dictionary into a pandas DataFrame
    data = []
    for report_id, report_data in reports_json.items():
        if not report_data["deletado"]:
            data.append({
                "ID": report_id,
                "Título": report_data["titulo"],
                "Descrição": report_data["descricao"],
                "Autor": report_data["autor"]
            })
    
    df = pd.DataFrame(data)
    
    # Display the DataFrame in Streamlit with clickable links
    st.write("### Relatórios Disponíveis")
    st.dataframe(df)
    
    # Make the DataFrame rows clickable
    selected_row = st.selectbox("Escolha um relatório", df["Título"])
    if selected_row:
        report_id = df[df["Título"] == selected_row]["ID"].values[0]
        load_and_execute_report(report_id, reports_json)

def main():
    st.set_page_config(page_title="Central de Relatórios", layout="wide")

    st.markdown("""
    <style>
    /* ========== SIDEBAR ========== */
    section[data-testid="stSidebar"] {
        color: #FFFFFF;
    }
    section[data-testid="stSidebar"] .stSelectbox div,
    section[data-testid="stSidebar"] .stMultiSelect div,
    section[data-testid="stSidebar"] label,
    section[data-testid="stSidebar"] span {
        color: #FFFFFF !important;
    }
    section[data-testid="stSidebar"] .stSlider > div > div,
    section[data-testid="stSidebar"] .stSlider label,
    section[data-testid="stSidebar"] .stSlider span {
        color: #FFFFFF !important;
    }
    section[data-testid="stSidebar"] h1,
    section[data-testid="stSidebar"] h2,
    section[data-testid="stSidebar"] h3,
    section[data-testid="stSidebar"] h4,
    section[data-testid="stSidebar"] h5,
    section[data-testid="stSidebar"] h6,
    section[data-testid="stSidebar"] p {
        color: #FFFFFF !important;
    }
    section[data-testid="stSidebar"] .css-1wa3eu0-placeholder {
        color: #FFFFFF !important;
    }
    /* ========== FORA DA SIDEBAR ========== */
    .stButton > button,
    .stSelectbox div,
    .stMultiSelect div,
    .stTextInput input,
    .stTextArea textarea {
        color: #FFFFFF !important;
    }
    .css-1d391kg, .css-1cpxqw2 {
        color: #FFFFFF !important;
    }
    label, .stSelectbox label {
        color: #1D345B !important;
        font-weight: bold;
    }
    .stSelectbox > div {
        border: 1px solid #D32F2F !important;
        border-radius: 8px;
    }
    .css-1n76uvr-option {
        color: #1D345B !important;
    }
    </style>
    """, unsafe_allow_html=True)

    # Sidebar logo
    logo_url = "https://d28lvm9jkyfotx.cloudfront.net/logo.png"
    target_url = "https://dataiesb.com"
    st.sidebar.markdown(
        f"""
        <a href="{target_url}" target="_blank">
            <img src="{logo_url}" style="width:100%; margin-bottom: 2rem;">
        </a>
        """,
        unsafe_allow_html=True
    )

    # Load reports.json
    reports_json = load_reports_json()

    # Determine if a report is selected
    report_id = st.query_params.get("id")

    if report_id:
        load_and_execute_report(report_id, reports_json)
    else:
        show_homepage(reports_json)

if __name__ == "__main__":
    main()

