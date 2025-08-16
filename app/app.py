import streamlit as st
import pandas as pd
import boto3
import json
import tempfile
import s3fs
import os
import shutil
import time

S3_BUCKET = "dataiesb-reports"
DYNAMODB_TABLE = "dataiesb-reports"
AWS_REGION = "us-east-1"

# Initialize AWS clients with error handling
try:
    s3_client = boto3.client('s3', region_name=AWS_REGION)
    dynamodb = boto3.resource('dynamodb', region_name=AWS_REGION)
    table = dynamodb.Table(DYNAMODB_TABLE)
    
    # Initialize S3 file system for pandas
    fs = s3fs.S3FileSystem()
except Exception as e:
    st.error(f"❌ Erro ao inicializar clientes AWS: {e}")
    s3_client = None
    dynamodb = None
    table = None
    fs = None

# Debug AWS credentials (only show in development)
try:
    import os
    if os.getenv('DEBUG_AWS_CREDS', 'false').lower() == 'true':
        session = boto3.Session()
        credentials = session.get_credentials()
        st.info(f"🔍 AWS Credentials Debug:")
        st.info(f"   - Access Key: {credentials.access_key[:8]}..." if credentials.access_key else "   - Access Key: None")
        st.info(f"   - Region: {AWS_REGION}")
        st.info(f"   - Profile: {session.profile_name}")
except Exception as e:
    pass  # Ignore credential debug errors

def cleanup_old_temp_files():
    """Clean up old temporary files on startup"""
    try:
        tmp_dir = os.path.join(os.getcwd(), "tmp")
        if os.path.exists(tmp_dir):
            for filename in os.listdir(tmp_dir):
                file_path = os.path.join(tmp_dir, filename)
                if os.path.isfile(file_path):
                    # Remove files older than 1 hour
                    file_age = time.time() - os.path.getmtime(file_path)
                    if file_age > 3600:  # 1 hour in seconds
                        os.remove(file_path)
                        print(f"Removed old temp file: {filename}")
    except Exception as e:
        print(f"Error cleaning up temp files: {e}")

def load_reports_from_dynamodb():
    """Fetch reports from DynamoDB table"""
    if not table:
        st.error("❌ Cliente DynamoDB não inicializado")
        return {}
        
    try:
        # Scan the DynamoDB table to get all reports
        response = table.scan()
        reports_data = {}
        processed_count = 0
        error_count = 0
        
        # Convert DynamoDB response to the same format as the original JSON
        for item in response['Items']:
            try:
                report_id = item.get('report_id')
                if not report_id:
                    st.warning(f"⚠️ Item sem report_id encontrado, pulando...")
                    error_count += 1
                    continue
                
                # Check for missing fields and provide defaults
                missing_fields = []
                if 'id_s3' not in item:
                    missing_fields.append('id_s3')
                if 'deletado' not in item:
                    missing_fields.append('deletado')
                    
                if missing_fields:
                    st.info(f"ℹ️ Relatório {report_id} tem campos faltando: {missing_fields}. Usando valores padrão.")
                    
                reports_data[report_id] = {
                    'id_s3': item.get('id_s3', f"{report_id}/"),  # Default to report_id/
                    'titulo': item.get('titulo', 'Título não disponível'),
                    'descricao': item.get('descricao', 'Descrição não disponível'),
                    'autor': item.get('autor', 'Autor não informado'),
                    'deletado': item.get('deletado', False),  # Default to False
                    'user_email': item.get('user_email', ''),
                    'created_at': item.get('created_at', ''),
                    'updated_at': item.get('updated_at', '')
                }
                processed_count += 1
                
            except Exception as item_error:
                error_count += 1
                st.warning(f"⚠️ Erro ao processar item {item.get('report_id', 'unknown')}: {item_error}")
                continue
        
        if processed_count > 0:
            st.success(f"✅ Carregados {processed_count} relatórios do DynamoDB")
        if error_count > 0:
            st.warning(f"⚠️ {error_count} itens tiveram problemas durante o carregamento")
            
        return reports_data
        
    except Exception as e:
        st.error(f"❌ Erro ao carregar relatórios do DynamoDB: {e}")
        st.error(f"Tipo do erro: {type(e).__name__}")
        
        # Check if error debug is enabled in sidebar
        try:
            # This will work if the sidebar has been rendered
            if st.session_state.get("error_debug", False):
                st.exception(e)
        except:
            # Fallback if session state is not available yet
            pass
            
        return {}

def list_reports_in_dynamodb(reports_data):
    """List reports from the loaded DynamoDB data"""
    return [report_id for report_id in reports_data if not reports_data[report_id]["deletado"]]

def load_and_execute_report(report_id, reports_data):
    """Download and execute the main.py script from S3"""
    if not s3_client:
        st.error("❌ Cliente S3 não inicializado")
        return
        
    tmp_dir = None
    try:
        # Debug info
        if st.session_state.get("show_debug", False):
            st.info(f"🔍 Debug: Carregando relatório ID {report_id}")
        
        # Look up the report by its ID in the data
        report = reports_data.get(str(report_id))
        if not report:
            st.error(f"❌ Relatório não encontrado para o ID: {report_id}")
            return
        
        # Get the S3 path for the main.py script
        s3_key = f"{report_id}/main.py"
        
        if st.session_state.get("show_debug", False):
            st.info(f"🔍 Debug: Buscando arquivo S3: {s3_key}")
        
        # Check if the object exists in S3 before attempting to download
        try:
            response = s3_client.head_object(Bucket=S3_BUCKET, Key=s3_key)
            if st.session_state.get("show_debug", False):
                file_size = response.get('ContentLength', 0)
                st.info(f"🔍 Debug: Arquivo encontrado, tamanho: {file_size} bytes")
        except s3_client.exceptions.NoSuchKey:
            st.error(f"❌ Arquivo não encontrado no S3: {s3_key}")
            return
        except Exception as head_error:
            st.error(f"❌ Erro ao verificar arquivo no S3: {head_error}")
            return
        
        # Create tmp directory if it doesn't exist
        tmp_dir = os.path.join(os.getcwd(), "tmp")
        os.makedirs(tmp_dir, exist_ok=True)
        
        # Create temporary file in tmp/ folder
        tmp_file_path = os.path.join(tmp_dir, f"report_{report_id}_main.py")
        
        if st.session_state.get("show_debug", False):
            st.info(f"🔍 Debug: Salvando em: {tmp_file_path}")
        
        # Download file from S3
        with open(tmp_file_path, "wb") as tmp_file:
            s3_client.download_fileobj(S3_BUCKET, s3_key, tmp_file)

        # Read the code
        with open(tmp_file_path, "r", encoding="utf-8") as f:
            code = f.read()
        
        if st.session_state.get("show_debug", False):
            st.info(f"🔍 Debug: Código carregado, {len(code)} caracteres")
        
        # Create execution context with necessary imports and variables
        # Create a modified streamlit object that prevents set_page_config calls
        class StreamlitWrapper:
            def __init__(self, original_st):
                self._st = original_st
            
            def __getattr__(self, name):
                if name == 'set_page_config':
                    # Return a no-op function for set_page_config
                    return lambda *args, **kwargs: None
                return getattr(self._st, name)
        
        st_wrapper = StreamlitWrapper(st)
        
        exec_globals = {
            "__name__": "__main__",
            "st": st_wrapper,  # Use the wrapper instead of original st
            "pd": pd,
            "boto3": boto3,
            "s3_client": s3_client,
            "S3_BUCKET": S3_BUCKET,
            "AWS_REGION": AWS_REGION,
            "s3fs": s3fs,
            "fs": fs,
            "os": os,
            "tempfile": tempfile
        }
        
        # Import additional modules that might be needed
        try:
            import plotly.express as px
            import plotly.io as pio
            exec_globals["px"] = px
            exec_globals["pio"] = pio
        except ImportError:
            pass
        
        if st.session_state.get("show_debug", False):
            st.info(f"🔍 Debug: Executando código do relatório...")
            
        exec(code, exec_globals)
        
        if st.session_state.get("show_debug", False):
            st.success(f"✅ Debug: Relatório executado com sucesso!")
        
    except Exception as e:
        st.error(f"❌ Erro ao carregar o relatório '{report_id}': {e}")
        
        # Show detailed error if error debug is enabled
        if st.session_state.get("error_debug", False):
            st.exception(e)
        else:
            st.error(f"Tipo do erro: {type(e).__name__}")
            st.info("💡 Ative 'Error Debug' na barra lateral para ver detalhes completos")
            
    finally:
        # Clean up temporary files
        if tmp_dir and os.path.exists(tmp_dir):
            try:
                # Remove all files in tmp directory
                files_removed = 0
                for filename in os.listdir(tmp_dir):
                    file_path = os.path.join(tmp_dir, filename)
                    if os.path.isfile(file_path):
                        os.remove(file_path)
                        files_removed += 1
                
                if st.session_state.get("show_debug", False) and files_removed > 0:
                    st.info(f"🗑️ Debug: {files_removed} arquivo(s) temporário(s) removido(s)")
                    
            except Exception as cleanup_error:
                st.warning(f"⚠️ Erro ao limpar arquivos temporários: {cleanup_error}")

def show_homepage(reports_data):
    st.title("Central de Relatórios Dinâmicos 📊")
    st.markdown("Escolha um relatório abaixo.")
    
    # Convert the reports_data dictionary into a pandas DataFrame
    data = []
    for report_id, report_data in reports_data.items():
        if not report_data["deletado"]:
            report_link = f"http://app.dataiesb.com/report/?id={report_id}"  # Fixed URL format
            data.append({
                "ID": report_id,
                "Título": report_data["titulo"],
                "Descrição": report_data["descricao"],
                "Autor": report_data["autor"],
                "Link": report_link  # Store raw link for later use
            })
    
    if not data:
        st.warning("Nenhum relatório ativo encontrado.")
        return
    
    df = pd.DataFrame(data)

    # Display the DataFrame in the main area
    st.write("### Relatórios Disponíveis")
    st.dataframe(df.drop(columns=["Link"]))  # Display without the link column
    
    # Adding links to the sidebar dynamically
    st.sidebar.title("Menu de Relatórios")
    for _, row in df.iterrows():
        report_link = row["Link"]
        st.sidebar.markdown(f"[{row['Título']}]({report_link})")  # Add clickable link to the sidebar

    # Make the DataFrame rows clickable - FIXED: Add default option
    report_options = ["Selecione um relatório..."] + df["Título"].tolist()
    selected_row = st.selectbox("Escolha um relatório", report_options)
    
    if selected_row and selected_row != "Selecione um relatório...":
        report_id = df[df["Título"] == selected_row]["ID"].values[0]
        st.info(f"Carregando relatório: {selected_row} (ID: {report_id})")
        load_and_execute_report(report_id, reports_data)

def main():
    st.set_page_config(page_title="Central de Relatórios", layout="wide")
    
    # Clean up old temporary files on startup
    cleanup_old_temp_files()

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

    # Debug info in sidebar
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 🔍 Debug Information")
    
    if st.sidebar.checkbox("Show Debug Info", key="show_debug"):
        st.sidebar.write(f"**Total reports:** {len(reports_data)}")
        active_count = len([r for r in reports_data.values() if not r["deletado"]])
        deleted_count = len(reports_data) - active_count
        st.sidebar.write(f"**Active reports:** {active_count}")
        st.sidebar.write(f"**Deleted reports:** {deleted_count}")
        
        # AWS Client Status
        st.sidebar.write("**AWS Clients:**")
        st.sidebar.write(f"  - S3 Client: {'✅ OK' if s3_client else '❌ Failed'}")
        st.sidebar.write(f"  - DynamoDB: {'✅ OK' if table else '❌ Failed'}")
        st.sidebar.write(f"  - S3FS: {'✅ OK' if fs else '❌ Failed'}")
        
        # Environment Info
        st.sidebar.write("**Environment:**")
        st.sidebar.write(f"  - Region: {AWS_REGION}")
        st.sidebar.write(f"  - S3 Bucket: {S3_BUCKET}")
        st.sidebar.write(f"  - DynamoDB Table: {DYNAMODB_TABLE}")
        
        # Temp Directory Status
        tmp_dir = os.path.join(os.getcwd(), "tmp")
        tmp_exists = os.path.exists(tmp_dir)
        st.sidebar.write(f"**Temp Directory:** {'✅ Exists' if tmp_exists else '❌ Missing'}")
        
        if tmp_exists:
            try:
                tmp_files = os.listdir(tmp_dir)
                st.sidebar.write(f"  - Files in tmp/: {len(tmp_files)}")
                if tmp_files:
                    st.sidebar.write("  - Files:")
                    for file in tmp_files[:5]:  # Show max 5 files
                        st.sidebar.write(f"    • {file}")
                    if len(tmp_files) > 5:
                        st.sidebar.write(f"    • ... and {len(tmp_files) - 5} more")
            except Exception as e:
                st.sidebar.write(f"  - Error reading tmp/: {e}")
    
    # Advanced Debug Options
    if st.sidebar.checkbox("Advanced Debug", key="advanced_debug"):
        st.sidebar.markdown("#### 📊 Report Details")
        for report_id, report in list(reports_data.items())[:3]:  # Show first 3 reports
            status = "🗑️ DELETED" if report['deletado'] else "✅ ACTIVE"
            st.sidebar.write(f"**{report_id}:** {status}")
            st.sidebar.write(f"  - Title: {report['titulo'][:20]}...")
            st.sidebar.write(f"  - Author: {report['autor'][:15]}...")
            st.sidebar.write(f"  - S3 Path: {report['id_s3']}")
        
        if len(reports_data) > 3:
            st.sidebar.write(f"... and {len(reports_data) - 3} more reports")
    
    # Error Debug (only show if there were errors)
    if st.sidebar.checkbox("Error Debug", key="error_debug"):
        st.sidebar.markdown("#### 🐛 Error Information")
        st.sidebar.write("Enable this to see detailed error traces when they occur.")
        st.sidebar.write("Errors will be displayed in the main area.")

    # Old debug info (keep for compatibility)
    if st.sidebar.checkbox("Legacy Debug Info", key="legacy_debug"):
        st.sidebar.write(f"Total reports: {len(reports_data)}")
        active_count = len([r for r in reports_data.values() if not r["deletado"]])
        st.sidebar.write(f"Active reports: {active_count}")

    # Determine if a report is selected
    report_id = st.query_params.get("id")

    if report_id:
        st.info(f"Loading report from URL parameter: {report_id}")
        load_and_execute_report(report_id, reports_data)
    else:
        show_homepage(reports_data)

if __name__ == "__main__":
    main()
