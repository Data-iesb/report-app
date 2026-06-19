"""
Simplified Central de Relatórios
Each report has its own TOML configuration for styling.
Only displays: title, description, author from DynamoDB + sidebar logo.
"""

import streamlit as st
import pandas as pd
import boto3
import os
import shutil
import tempfile
import toml

# AWS Configuration
S3_BUCKET = "dataiesb-reports"
DYNAMODB_TABLE = "dataiesb-reports"
AWS_REGION = "us-east-1"

# Initialize AWS clients
try:
    s3_client = boto3.client('s3', region_name=AWS_REGION)
    dynamodb = boto3.resource('dynamodb', region_name=AWS_REGION)
    table = dynamodb.Table(DYNAMODB_TABLE)
except Exception as e:
    st.error(f"❌ Erro ao inicializar clientes AWS: {e}")
    s3_client = None
    dynamodb = None
    table = None

def apply_report_toml_config(report_id):
    """Apply TOML configuration for a specific report if it exists"""
    if not s3_client:
        return False
        
    try:
        config_key = f"{report_id}/config.toml"
        
        # Check if config.toml exists for this report
        s3_client.head_object(Bucket=S3_BUCKET, Key=config_key)
        
        # Download the TOML config
        config_content = s3_client.get_object(Bucket=S3_BUCKET, Key=config_key)['Body'].read().decode('utf-8')
        
        # Parse TOML
        config_data = toml.loads(config_content)
        
        # Apply only Streamlit configuration sections
        streamlit_config = {}
        for section in ['theme', 'server', 'browser', 'runner', 'logger', 'client']:
            if section in config_data:
                streamlit_config[section] = config_data[section]
        
        if streamlit_config:
            # Write to .streamlit/config.toml
            config_dir = os.path.join(os.getcwd(), ".streamlit")
            os.makedirs(config_dir, exist_ok=True)
            config_path = os.path.join(config_dir, "config.toml")
            
            with open(config_path, 'w') as f:
                toml.dump(streamlit_config, f)
            
            return True
            
    except s3_client.exceptions.NoSuchKey:
        # No custom config for this report
        return False
    except Exception as e:
        st.warning(f"⚠️ Erro ao carregar configuração TOML: {e}")
        return False
    
    return False

def load_reports_from_dynamodb():
    """Fetch reports from DynamoDB table"""
    if not table:
        return {}
        
    try:
        response = table.scan()
        reports_data = {}
        
        for item in response['Items']:
            report_id = item.get('report_id')
            if report_id and not item.get('deletado', False):
                reports_data[report_id] = {
                    'titulo': item.get('titulo', 'Dashboard'),
                    'descricao': item.get('descricao', 'Análise de dados'),
                    'autor': item.get('autor', 'Desenvolvedor')
                }
        
        return reports_data
        
    except Exception as e:
        st.error(f"❌ Erro ao carregar relatórios: {e}")
        return {}

def render_report_header(report_data):
    """Render simple report header"""
    st.title(report_data['titulo'])
    st.markdown(f"*{report_data['descricao']}*")
    st.markdown(f"**👨💻 Desenvolvido por:** {report_data['autor']}")
    st.markdown("---")

def load_and_execute_report(report_id, reports_data):
    """Load and execute report with its TOML configuration"""
    if not s3_client or report_id not in reports_data:
        st.error("❌ Relatório não encontrado")
        return
        
    try:
        # Apply TOML configuration for this report
        config_applied = apply_report_toml_config(report_id)
        if config_applied:
            st.info(f"🎨 Configuração personalizada carregada para o relatório {report_id}")
        
        # Render header with report metadata
        render_report_header(reports_data[report_id])
        
        # Download and execute main.py
        main_py_key = f"{report_id}/main.py"
        
        # Check if main.py exists
        s3_client.head_object(Bucket=S3_BUCKET, Key=main_py_key)
        
        # Download main.py
        response = s3_client.get_object(Bucket=S3_BUCKET, Key=main_py_key)
        code = response['Body'].read().decode('utf-8')
        
        # Execute the code
        exec_globals = {
            "__name__": "__main__",
            "st": st,
            "pd": pd,
            "boto3": boto3,
            "s3_client": s3_client,
            "S3_BUCKET": S3_BUCKET,
            "AWS_REGION": AWS_REGION,
            "os": os,
            "tempfile": tempfile
        }
        
        # Add common imports
        try:
            import plotly.express as px
            import plotly.io as pio
            exec_globals["px"] = px
            exec_globals["pio"] = pio
        except ImportError:
            pass
        
        exec(code, exec_globals)
        
    except s3_client.exceptions.NoSuchKey:
        st.error(f"❌ Arquivo main.py não encontrado: {main_py_key}")
    except Exception as e:
        st.error(f"❌ Erro ao executar relatório: {e}")

def show_homepage(reports_data):
    """Show homepage with list of available reports"""
    st.title("Central de Relatórios 📊")
    st.markdown("Escolha um relatório abaixo:")
    
    if not reports_data:
        st.warning("Nenhum relatório encontrado.")
        return
    
    # Create DataFrame for display
    data = []
    for report_id, report_data in reports_data.items():
        data.append({
            "ID": report_id,
            "Título": report_data["titulo"],
            "Descrição": report_data["descricao"],
            "Desenvolvido por": report_data["autor"]
        })
    
    df = pd.DataFrame(data)
    st.dataframe(df, use_container_width=True)
    
    # Report selector
    report_options = ["Selecione um relatório..."] + df["Título"].tolist()
    selected_report = st.selectbox("Escolha um relatório", report_options)
    
    if selected_report and selected_report != "Selecione um relatório...":
        report_id = df[df["Título"] == selected_report]["ID"].values[0]
        load_and_execute_report(report_id, reports_data)

def main():
    # Basic page config
    st.set_page_config(
        page_title="Central de Relatórios", 
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
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
    
    # Check if specific report is requested
    report_id = st.query_params.get("id")
    
    if report_id and report_id in reports_data:
        load_and_execute_report(report_id, reports_data)
    else:
        show_homepage(reports_data)

if __name__ == "__main__":
    main()
