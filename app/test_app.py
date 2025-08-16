import streamlit as st
import pandas as pd
import boto3

# Configuration
S3_BUCKET = "dataiesb-reports"
DYNAMODB_TABLE = "dataiesb-reports"
AWS_REGION = "us-east-1"

# AWS clients
s3_client = boto3.client('s3', region_name=AWS_REGION)
dynamodb = boto3.resource('dynamodb', region_name=AWS_REGION)
table = dynamodb.Table(DYNAMODB_TABLE)

def load_reports_from_dynamodb():
    """Fetch reports from DynamoDB table"""
    try:
        response = table.scan()
        reports_data = {}
        
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

def main():
    st.set_page_config(page_title="Test Central de Relatórios", layout="wide")
    
    st.title("Test - Central de Relatórios Dinâmicos 📊")
    
    # Load reports
    reports_data = load_reports_from_dynamodb()
    st.write(f"**Debug:** Loaded {len(reports_data)} total reports")
    
    # Show raw data for debugging
    if st.checkbox("Show raw data"):
        st.json(reports_data)
    
    # Filter active reports
    active_data = []
    for report_id, report_data in reports_data.items():
        if not report_data["deletado"]:
            active_data.append({
                "ID": report_id,
                "Título": report_data["titulo"],
                "Descrição": report_data["descricao"],
                "Autor": report_data["autor"]
            })
    
    st.write(f"**Debug:** Found {len(active_data)} active reports")
    
    if active_data:
        df = pd.DataFrame(active_data)
        st.write("### Relatórios Disponíveis")
        st.dataframe(df)
        
        # Simple selectbox test
        report_titles = df["Título"].tolist()
        selected_title = st.selectbox("Escolha um relatório", ["Selecione..."] + report_titles)
        
        if selected_title != "Selecione...":
            selected_id = df[df["Título"] == selected_title]["ID"].values[0]
            st.success(f"Você selecionou o relatório ID: {selected_id}")
            
            # Test S3 file access
            s3_key = f"{selected_id}/main.py"
            try:
                response = s3_client.head_object(Bucket=S3_BUCKET, Key=s3_key)
                st.success(f"✅ Arquivo main.py encontrado no S3 para o relatório {selected_id}")
                
                # Try to download and show first few lines
                if st.button("Preview código"):
                    try:
                        obj = s3_client.get_object(Bucket=S3_BUCKET, Key=s3_key)
                        code = obj['Body'].read().decode('utf-8')
                        st.code(code[:500] + "..." if len(code) > 500 else code, language="python")
                    except Exception as e:
                        st.error(f"Erro ao baixar código: {e}")
                        
            except Exception as e:
                st.error(f"❌ Erro ao verificar arquivo no S3: {e}")
    else:
        st.warning("Nenhum relatório ativo encontrado")

if __name__ == "__main__":
    main()
