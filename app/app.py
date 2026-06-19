"""
Central de Relatórios Dinâmicos - MIV-Compliant Application

This application implements the MIV (Marca de Identidade Visual) color palette
and advanced text visibility system to ensure optimal accessibility and brand compliance.

MIV Color Palette:
- Primary Blue (#1D345B): Main text, backgrounds, primary elements
- Accent Red (#D13F42): Highlights, primary buttons, important actions
- White (#FFFFFF): Main background, text on dark backgrounds
- Gray (#E4E4E4): Secondary elements, borders, subtle backgrounds
- Black (#000000): Code blocks, high contrast elements

Advanced Features:
1. Intelligent Text Visibility: Automatic contrast adjustment based on background
2. Canvas Protection: Preserves interactive visualizations (maps, charts)
3. Accessibility Compliance: WCAG 2.1 AA standards
4. Responsive Design: Mobile and desktop optimized
5. Development Environment: Live code testing with MIV styling

Text Visibility Rules:
- White backgrounds → Blue text (#1D345B)
- Blue backgrounds → White text (#FFFFFF)
- Red backgrounds → White text (#FFFFFF)
- Gray backgrounds → Blue text (#1D345B)
- Black backgrounds → White text (#FFFFFF)

Author: Amazon Q Developer
Version: 2.0 - MIV Compliant
Last Updated: 2025-08-17
"""

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
    """Apply only report header CSS - let TOML handle everything else"""
    load_css_file("style.css")

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
                    error_count += 1
                    continue
                    
                reports_data[report_id] = {
                    'id_s3': item.get('id_s3', f"{report_id}/"),
                    'titulo': item.get('titulo', 'Título não disponível'),
                    'descricao': item.get('descricao', 'Descrição não disponível'),
                    'autor': item.get('autor', 'Autor não informado'),
                    'deletado': item.get('deletado', False),
                    'user_email': item.get('user_email', ''),
                    'created_at': item.get('created_at', ''),
                    'updated_at': item.get('updated_at', '')
                }
                processed_count += 1
                
            except Exception as item_error:
                error_count += 1
                continue
        
        # No success messages - silent loading
        return reports_data
        
    except Exception as e:
        st.error(f"❌ Erro ao carregar relatórios do DynamoDB: {e}")
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
        # Look up the report by its ID in the data
        report = reports_data.get(str(report_id))
        if not report:
            st.error(f"❌ Relatório não encontrado para o ID: {report_id}")
            return
        
        # Render dashboard header
        render_dashboard_header(report)
        
        # Get the S3 path for the main.py script
        s3_key = f"{report_id}/main.py"
        
        # Check if the object exists in S3 before attempting to download
        try:
            response = s3_client.head_object(Bucket=S3_BUCKET, Key=s3_key)
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
        
        # Download file from S3
        with open(tmp_file_path, "wb") as tmp_file:
            s3_client.download_fileobj(S3_BUCKET, s3_key, tmp_file)

        # Read the code
        with open(tmp_file_path, "r", encoding="utf-8") as f:
            code = f.read()
        
        # Create execution context with necessary imports and variables
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
            
        exec(code, exec_globals)
        
        # Render dashboard footer
        render_dashboard_footer(report)
        
    except Exception as e:
        st.error(f"❌ Erro ao carregar o relatório '{report_id}': {e}")
            
    finally:
        # Clean up temporary files
        if tmp_dir and os.path.exists(tmp_dir):
            try:
                # Remove all files in tmp directory
                for filename in os.listdir(tmp_dir):
                    file_path = os.path.join(tmp_dir, filename)
                    if os.path.isfile(file_path):
                        os.remove(file_path)
                    
            except Exception as cleanup_error:
                pass  # Silent cleanup

def show_homepage(reports_data):
    st.title("Central de Relatórios Dinâmicos 📊")
    st.markdown("Escolha um relatório abaixo.")
    
    # Convert the reports_data dictionary into a pandas DataFrame
    data = []
    for report_id, report_data in reports_data.items():
        if not report_data["deletado"]:
            report_link = f"http://app.dataiesb.com/report/?id={report_id}"
            data.append({
                "ID": report_id,
                "Título": report_data["titulo"],
                "Descrição": report_data["descricao"],
                "Autor": report_data["autor"],
                "Link": report_link
            })
    
    if not data:
        st.warning("Nenhum relatório ativo encontrado.")
        return
    
    df = pd.DataFrame(data)

    # Display the DataFrame in the main area
    st.write("### Relatórios Disponíveis")
    st.dataframe(df.drop(columns=["Link"]))
    
    # Adding links to the sidebar dynamically
    st.sidebar.title("Menu de Relatórios")
    for _, row in df.iterrows():
        report_link = row["Link"]
        st.sidebar.markdown(f"[{row['Título']}]({report_link})")

    # Make the DataFrame rows clickable
    report_options = ["Selecione um relatório..."] + df["Título"].tolist()
    selected_row = st.selectbox("Escolha um relatório", report_options)
    
    if selected_row and selected_row != "Selecione um relatório...":
        report_id = df[df["Título"] == selected_row]["ID"].values[0]
        load_and_execute_report(report_id, reports_data)

def show_dev_environment():
    """Development environment - for testing dashboards only"""
    
    st.title("🛠️ Development Environment")
    st.markdown("Test your dashboard code here")
    st.markdown("---")
    
    # Code editor
    code_input = st.text_area(
        "Dashboard Code",
        value="",
        height=300,
        placeholder="""# Test your dashboard code here
import streamlit as st
import pandas as pd

st.title("My Dashboard")
st.write("Test your dashboard components")

# Sample data
data = {'A': [1, 2, 3], 'B': [4, 5, 6]}
df = pd.DataFrame(data)
st.dataframe(df)

# Sample chart
st.line_chart(df)

# Sample metrics
col1, col2 = st.columns(2)
with col1:
    st.metric("Metric 1", "100", "10%")
with col2:
    st.metric("Metric 2", "200", "-5%")
""",
        key="dev_code_input"
    )
    
    # Action buttons
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("🚀 Run Dashboard", type="primary"):
            if code_input.strip():
                st.session_state.dev_code_to_run = code_input
                st.rerun()
            else:
                st.warning("Please enter some code to run.")
    
    with col2:
        if st.button("🗑️ Clear"):
            st.session_state.dev_code_input = ""
            if "dev_code_to_run" in st.session_state:
                del st.session_state.dev_code_to_run
            st.rerun()
    
    # Preview section
    st.markdown("---")
    st.subheader("📊 Dashboard Preview")
    
    # Execute code if available
    if "dev_code_to_run" in st.session_state and st.session_state.dev_code_to_run:
        try:
            with st.container():
                # Execute the user code
                exec_globals = {
                    'st': st,
                    'pd': pd,
                }
                
                # Add common imports
                try:
                    import numpy as np
                    exec_globals['np'] = np
                except ImportError:
                    pass
                
                try:
                    import plotly.express as px
                    exec_globals['px'] = px
                except ImportError:
                    pass
                
                # Execute the user code
                exec(st.session_state.dev_code_to_run, exec_globals)
            
            st.success("✅ Dashboard executed successfully!")
            
        except Exception as e:
            st.error(f"❌ Error executing dashboard: {str(e)}")
    else:
        st.info("👆 Enter dashboard code above and click 'Run Dashboard' to see results")
        
        # Show simple example
        st.markdown("### Example Dashboard")
        st.info("ℹ️ This is a sample info box")
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Sample Metric", "42", "5%")
        with col2:
            if st.button("Sample Button"):
                st.success("Button clicked!")

def main():
    # Set page config with MIV colors - this must be first
    st.set_page_config(
        page_title="Central de Relatórios", 
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Apply minimal styling - TOML handles text visibility
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

    # Determine if a report is selected or dev environment is requested
    report_id = st.query_params.get("id")
    dev_path = st.query_params.get("path")

    if dev_path == "dev":
        # Show development environment
        show_dev_environment()
    elif report_id:
        load_and_execute_report(report_id, reports_data)
    else:
        show_homepage(reports_data)

if __name__ == "__main__":
    main()
