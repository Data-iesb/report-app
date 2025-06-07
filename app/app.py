import streamlit as st
import boto3
import tempfile

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
    """Download and execute a main.py script from S3"""
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

    # ✅ Load external CSS from S3
    css_url = "https://dataiesb-site.s3.us-east-1.amazonaws.com/style.css"
    st.markdown(f'<link href="{css_url}" rel="stylesheet">', unsafe_allow_html=True)

    # ✅ Sidebar logo with link
    logo_url = "https://dataiesb-site.s3.us-east-1.amazonaws.com/logo.png"
    target_url = "http://k8s-default-ingressi-73bd0705e3-102651203.sa-east-1.elb.amazonaws.com/"
    st.sidebar.markdown(
        f"""
        <a href="{target_url}" target="_blank">
            <img src="{logo_url}" style="width:100%; margin-bottom: 2rem;">
        </a>
        """,
        unsafe_allow_html=True
    )

    # ✅ Fetch available reports
    reports = list_reports_in_s3()

    # ✅ Layout for the homepage
    report_id = st.query_params.get("rel")

    if report_id:
        st.markdown(f"### Carregando relatório: `{report_id}`")
        load_and_execute_report(report_id)
    else:
        st.markdown("<div style='text-align: center;'>", unsafe_allow_html=True)
        st.title("Central de Relatórios Dinâmicos 📊")
        st.markdown("Escolha um relatório abaixo.")
        st.markdown("</div>", unsafe_allow_html=True)

        st.markdown("<h3 style='text-align: center; margin-top: 3rem;'>Relatórios Disponíveis</h3>", unsafe_allow_html=True)

        for r in reports:
            st.markdown(
                f"""
                <div style='text-align: center; margin-bottom: 10px;'>
                    <a href="?rel={r}" style="color:#0d6efd; font-size:18px; text-decoration:none;">
                        📄 {r.replace('-', ' ').title()}
                    </a>
                </div>
                """,
                unsafe_allow_html=True
            )


if __name__ == "__main__":
    main()

