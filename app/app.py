import streamlit as st
import pandas as pd
import boto3
import json
import tempfile  # <-- Add this import

S3_BUCKET = "dataiesb"
DYNAMODB_TABLE = "dataiesb-reports"

s3_client = boto3.client('s3')
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table(DYNAMODB_TABLE)

def load_reports_from_dynamodb():
    """Fetch reports from DynamoDB table"""
    try:
        # Scan the DynamoDB table to get all reports
        response = table.scan()
        reports_data = {}
        
        # Convert DynamoDB response to the same format as the original JSON
        for item in response['Items']:
            report_id = item['report_id']
            reports_data[report_id] = {
                'id_s3': item['id_s3'],
                'titulo': item['titulo'],
                'descricao': item['descricao'],
                'autor': item['autor'],
                'deletado': item['deletado'],
                'user_email': item['user_email'],
                'created_at': item['created_at'],
                'updated_at': item['updated_at']
            }
        
        return reports_data
    except Exception as e:
        st.error(f"❌ Erro ao carregar relatórios do DynamoDB: {e}")
        return {}

def list_reports_in_dynamodb(reports_data):
    """List reports from the loaded DynamoDB data"""
    return [report_id for report_id in reports_data if not reports_data[report_id]["deletado"]]

def load_and_execute_report(report_id, reports_data):
    """Download and execute the main.py script from S3"""
    try:
        # Look up the report by its ID in the data
        report = reports_data.get(str(report_id))
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

def show_homepage(reports_data):
    st.title("Central de Relatórios Dinâmicos 📊")
    st.markdown("Escolha um relatório abaixo.")
    
    # Convert the reports_data dictionary into a pandas DataFrame
    data = []
    for report_id, report_data in reports_data.items():
        if not report_data["deletado"]:
            report_link = f"https://dataiesb.com/reports/{report_id}"  # Create the link (adjust URL as necessary)
            data.append({
                "ID": report_id,
                "Título": report_data["titulo"],
                "Descrição": report_data["descricao"],
                "Autor": report_data["autor"],
                "Link": report_link  # Store raw link for later use
            })
    
    df = pd.DataFrame(data)

    # Display the DataFrame in the main area
    st.write("### Relatórios Disponíveis")
    st.dataframe(df.drop(columns=["Link"]))  # Display without the link column
    
    # Adding links to the sidebar dynamically
    st.sidebar.title("Menu de Relatórios")
    for _, row in df.iterrows():
        report_link = row["Link"]
        st.sidebar.markdown(f"[{row['Título']}]({report_link})")  # Add clickable link to the sidebar

    # Make the DataFrame rows clickable
    selected_row = st.selectbox("Escolha um relatório", df["Título"])
    if selected_row:
        report_id = df[df["Título"] == selected_row]["ID"].values[0]
        load_and_execute_report(report_id, reports_data)

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

    # Load reports from DynamoDB
    reports_data = load_reports_from_dynamodb()

    # Determine if a report is selected
    report_id = st.query_params.get("id")

    if report_id:
        load_and_execute_report(report_id, reports_data)
    else:
        show_homepage(reports_data)

if __name__ == "__main__":
    main()

