import streamlit as st
import boto3
import tempfile
import os

S3_BUCKET = "dataiesb-site"
s3_client = boto3.client("s3")

def list_reports_in_s3():
    """List all folders in S3 that contain main.py"""
    reports = []
    paginator = s3_client.get_paginator("list_objects_v2")
    for page in paginator.paginate(Bucket=S3_BUCKET):
        for obj in page.get("Contents", []):
            key = obj["Key"]
            if key.endswith("main.py"):
                report_id = key.rsplit("/", 1)[0]
                reports.append(report_id)
    return sorted(set(reports))

def load_and_execute_report(report_id):
    """Download main.py from S3 and execute it"""
    s3_key = f"{report_id}/main.py"
    try:
        with tempfile.NamedTemporaryFile(mode="wb", suffix=".py", delete=False) as tmp:
            s3_client.download_fileobj(S3_BUCKET, s3_key, tmp)
            tmp_path = tmp.name

        with open(tmp_path, "r") as f:
            code = f.read()
        exec(code, {"__name__": "__main__"})
    except Exception as e:
        st.error(f"❌ Erro ao carregar o relatório '{report_id}': {e}")

def main():
    st.set_page_config(page_title="Central de Relatórios", layout="wide")

    st.sidebar.image("logo.png", use_container_width=True)

    st.sidebar.markdown(
        """
        <h1 style="color: white; margin-top: 1rem;">
            📂 Relatórios Disponíveis
        </h1>
        """,
        unsafe_allow_html=True
    )

    reports = list_reports_in_s3()

    for r in reports:
        st.sidebar.markdown(
            f"""<a href="?rel={r}" style="color:white; text-decoration:none;">📄 {r.replace('-', ' ').title()}</a>""",
            unsafe_allow_html=True
         )


    report_id = st.query_params.get("rel")

    if report_id:
        #st.markdown(f"### Carregando relatório: `{report_id}`")
        load_and_execute_report(report_id)
    else:
        st.title("📊 - Central de Relatórios Dinâmicos")
        st.markdown("Escolha um relatório no menu à esquerda.")

if __name__ == "__main__":
    main()

