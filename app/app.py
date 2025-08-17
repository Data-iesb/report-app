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

# Debugging variable - set to False to disable debug output
debugging_bol = False

def render_dashboard_header(report_data):
    """Render the dashboard header with title and description"""
    titulo = report_data.get('titulo', 'Dashboard')
    descricao = report_data.get('descricao', 'Análise de dados interativa')
    
    st.markdown(f"""
    <div class="report-header">
        <h1 class="header-title">{titulo}</h1>
        <p class="header-desc">{descricao}</p>
    </div>
    """, unsafe_allow_html=True)

def render_dashboard_footer(report_data):
    """Render the dashboard footer with author information"""
    autor = report_data.get('autor', 'Autor não informado')
    created_at = report_data.get('created_at', '')
    updated_at = report_data.get('updated_at', '')
    
    # Format dates if available
    created_date = ""
    updated_date = ""
    
    if created_at:
        try:
            from datetime import datetime
            if isinstance(created_at, str):
                # Try to parse ISO format date
                dt = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
                created_date = dt.strftime('%d/%m/%Y')
        except:
            created_date = str(created_at)[:10]  # Fallback to first 10 chars
    
    if updated_at and updated_at != created_at:
        try:
            from datetime import datetime
            if isinstance(updated_at, str):
                dt = datetime.fromisoformat(updated_at.replace('Z', '+00:00'))
                updated_date = dt.strftime('%d/%m/%Y')
        except:
            updated_date = str(updated_at)[:10]
    
    # Use Streamlit native components for better compatibility
    st.markdown("---")
    
    # Create columns for footer info
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown(f"**👨‍💻 Desenvolvido por:** {autor}")
    
    with col2:
        if created_date:
            st.markdown(f"**📅 Criado em:** {created_date}")
    
    with col3:
        if updated_date:
            st.markdown(f"**🔄 Atualizado em:** {updated_date}")

def apply_custom_styles():
    """Apply custom CSS styles to the Streamlit app"""
    # Load external CSS file
    load_css_file("style.css")
    
    # Apply button styling but exclude canvas-based content like maps
    st.markdown("""
    <style>
    /* Style buttons but exclude any elements inside canvas containers */
    .stButton > button:not([data-canvas]):not([class*="canvas"]) {
        background-color: #2C5282 !important;
        color: white !important;
        border: 1px solid #2C5282 !important;
        border-radius: 6px !important;
    }
    
    .stButton > button:not([data-canvas]):not([class*="canvas"]):hover {
        background-color: #1D345B !important;
        color: white !important;
        border-color: #1D345B !important;
    }
    
    /* Exclude all canvas-related elements from any button styling */
    canvas,
    canvas *,
    [class*="canvas"],
    [class*="canvas"] *,
    [id*="canvas"],
    [id*="canvas"] *,
    .leaflet-container,
    .leaflet-container *,
    .folium-map,
    .folium-map *,
    iframe,
    iframe * {
        all: revert !important;
    }
    
    /* Specifically protect canvas buttons and controls */
    canvas button,
    canvas input,
    canvas a,
    [class*="canvas"] button,
    [class*="canvas"] input,
    [class*="canvas"] a {
        background: initial !important;
        color: initial !important;
        border: initial !important;
        border-radius: initial !important;
        font-weight: initial !important;
        box-shadow: initial !important;
    }
    </style>
    """, unsafe_allow_html=True)

def check_local_main():
    """Check if there's a local main.py file for development"""
    local_main_path = os.path.join(os.getcwd(), "main.py")
    return os.path.exists(local_main_path)

def load_and_execute_local_main():
    """Load and execute local main.py with template"""
    local_main_path = os.path.join(os.getcwd(), "main.py")
    
    try:
        # Create mock report data for local development
        mock_report_data = {
            'titulo': '🧪 Local Development Dashboard',
            'descricao': 'Dashboard em desenvolvimento local. Esta é uma simulação do ambiente de produção.',
            'autor': 'Desenvolvedor Local',
            'created_at': '2025-08-16T20:10:00Z',
            'updated_at': '2025-08-16T20:10:00Z'
        }
        
        # Render dashboard header
        render_dashboard_header(mock_report_data)
        
        # Read and execute the local main.py
        with open(local_main_path, "r", encoding="utf-8") as f:
            code = f.read()
        
        # Create execution context
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
            "st": st_wrapper,
            "pd": pd,
            "boto3": boto3,
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
        
        # Execute the local main.py
        exec(code, exec_globals)
        
        # Render dashboard footer
        render_dashboard_footer(mock_report_data)
        
        # Show local development notice
        st.info("🧪 **Modo de Desenvolvimento Local** - Este dashboard está sendo executado localmente. Para produção, faça upload para o S3.")
        
        return True
        
    except Exception as e:
        st.error(f"❌ Erro ao executar main.py local: {e}")
        st.error(f"Tipo do erro: {type(e).__name__}")
        return False

def load_css_file(css_file_path):
    """Load CSS file and inject it into Streamlit"""
    try:
        with open(css_file_path, 'r', encoding='utf-8') as f:
            css_content = f.read()
        st.markdown(f"<style>{css_content}</style>", unsafe_allow_html=True)
        return True
    except FileNotFoundError:
        st.warning(f"⚠️ CSS file not found: {css_file_path}")
        return False
    except Exception as e:
        st.error(f"❌ Error loading CSS file: {e}")
        return False

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
        missing_fields_reports = []
        
        # Convert DynamoDB response to the same format as the original JSON
        for item in response['Items']:
            try:
                report_id = item.get('report_id')
                if not report_id:
                    if st.session_state.get("show_debug", False):
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
                    missing_fields_reports.append((report_id, missing_fields))
                    # Only show individual messages in debug mode
                    if st.session_state.get("show_debug", False):
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
                if st.session_state.get("show_debug", False):
                    st.warning(f"⚠️ Erro ao processar item {item.get('report_id', 'unknown')}: {item_error}")
                continue
        
        # Show summary messages
        if processed_count > 0:
            # Only show success message in debug mode, or if there were issues
            if st.session_state.get("show_debug", False) or error_count > 0 or missing_fields_reports:
                st.success(f"✅ Carregados {processed_count} relatórios do DynamoDB")
        
        # Show summary of missing fields only in debug mode
        if missing_fields_reports and st.session_state.get("show_debug", False):
            st.info(f"ℹ️ {len(missing_fields_reports)} relatórios com campos faltando foram corrigidos com valores padrão")
        
        if error_count > 0:
            if st.session_state.get("show_debug", False):
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
        
        # Render dashboard header
        render_dashboard_header(report)
        
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
        
        # Render dashboard footer
        render_dashboard_footer(report)
        
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
        # Only show loading message in debug mode
        if st.session_state.get("show_debug", False):
            st.info(f"🔍 Debug: Carregando relatório: {selected_row} (ID: {report_id})")
        load_and_execute_report(report_id, reports_data)

def main():
    st.set_page_config(page_title="Central de Relatórios", layout="wide")
    
    # Apply custom styling
    apply_custom_styles()
    
    # Clean up old temporary files on startup
    cleanup_old_temp_files()

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

    # Debug info in sidebar - simplified
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 🔍 Debug Options")
    
    # Simple debug toggle
    show_debug = st.sidebar.checkbox("Show Debug Info", key="show_debug")
    
    if show_debug:
        st.sidebar.write(f"**Reports:** {len(reports_data)} total")
        active_count = len([r for r in reports_data.values() if not r["deletado"]])
        st.sidebar.write(f"**Active:** {active_count}")
        
        # AWS Status
        aws_status = "✅" if s3_client and table else "❌"
        st.sidebar.write(f"**AWS:** {aws_status}")
        
        # Advanced options (collapsed by default)
        if st.sidebar.expander("Advanced Debug"):
            st.sidebar.write(f"**Environment:**")
            st.sidebar.write(f"  - Region: {AWS_REGION}")
            st.sidebar.write(f"  - S3 Bucket: {S3_BUCKET}")
            
            # Error details toggle
            st.sidebar.checkbox("Show Error Details", key="error_debug")
            
            # Temp directory info
            tmp_dir = os.path.join(os.getcwd(), "tmp")
            if os.path.exists(tmp_dir):
                tmp_files = len(os.listdir(tmp_dir))
                st.sidebar.write(f"  - Temp files: {tmp_files}")
    
    # Keep error debug as separate option for when things go wrong
    if not show_debug:
        st.sidebar.checkbox("Show Error Details", key="error_debug")

    # Determine if a report is selected
    report_id = st.query_params.get("id")

    if report_id:
        # Only show loading message in debug mode
        if st.session_state.get("show_debug", False):
            st.info(f"🔍 Debug: Loading report from URL parameter: {report_id}")
        load_and_execute_report(report_id, reports_data)
    else:
        show_homepage(reports_data)

if __name__ == "__main__":
    main()
