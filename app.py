from datetime import date
from html import escape
from urllib.parse import quote

import streamlit as st
from fpdf import FPDF


st.set_page_config(
    page_title="Recibo Rapido",
    layout="centered",
    initial_sidebar_state="collapsed",
)


def money_cop(value: float) -> str:
    return f"$ {value:,.0f} COP".replace(",", ".")


def receipt_number(receipt_date: date, client_name: str) -> str:
    clean_name = "".join(char for char in client_name.upper() if char.isalnum())
    suffix = clean_name[:3] if clean_name else "CLI"
    return f"RC-{receipt_date.strftime('%Y%m%d')}-{suffix}"


def only_digits(value: str) -> str:
    return "".join(char for char in value if char.isdigit())


def clean_pdf_text(text: str) -> str:
    replacements = {
        "\u00e1": "a",
        "\u00e9": "e",
        "\u00ed": "i",
        "\u00f3": "o",
        "\u00fa": "u",
        "\u00c1": "A",
        "\u00c9": "E",
        "\u00cd": "I",
        "\u00d3": "O",
        "\u00da": "U",
        "\u00f1": "n",
        "\u00d1": "N",
    }
    for source, target in replacements.items():
        text = text.replace(source, target)
    return text


def build_pdf(
    client_name: str,
    client_phone: str,
    work_concept: str,
    total_value: float,
    receipt_date: date,
    technician_name: str,
    technician_phone: str,
    payment_method: str,
) -> bytes:
    receipt_id = receipt_number(receipt_date, client_name)

    pdf = FPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=18)

    pdf.set_fill_color(247, 249, 252)
    pdf.rect(0, 0, 210, 297, style="F")

    pdf.set_fill_color(255, 255, 255)
    pdf.rect(12, 12, 186, 258, style="F")

    pdf.set_fill_color(25, 35, 50)
    pdf.rect(12, 12, 186, 38, style="F")

    pdf.set_text_color(255, 255, 255)
    pdf.set_font("Arial", "B", 20)
    pdf.set_xy(20, 22)
    pdf.cell(0, 8, "RECIBO DE COBRO", ln=True)

    pdf.set_font("Arial", "", 10)
    pdf.set_x(20)
    pdf.cell(0, 7, "Servicios tecnicos y reparaciones - Barranquilla", ln=True)

    pdf.set_font("Arial", "B", 10)
    pdf.set_xy(146, 22)
    pdf.cell(44, 7, receipt_id, ln=True, align="R")
    pdf.set_font("Arial", "", 9)
    pdf.set_x(146)
    pdf.cell(44, 6, receipt_date.strftime("%d/%m/%Y"), ln=True, align="R")

    pdf.set_text_color(33, 37, 41)
    pdf.set_draw_color(220, 224, 229)
    pdf.set_line_width(0.4)

    pdf.set_y(62)
    pdf.set_x(20)
    pdf.set_font("Arial", "B", 11)
    pdf.cell(80, 8, "Cobrar a", ln=0)
    pdf.cell(80, 8, "Prestador del servicio", ln=1)

    pdf.set_font("Arial", "", 10)
    pdf.set_text_color(88, 99, 115)
    pdf.set_x(20)
    pdf.multi_cell(80, 7, clean_pdf_text(client_name), border=0)
    if client_phone:
        pdf.set_x(20)
        pdf.set_font("Arial", "", 9)
        pdf.multi_cell(80, 6, clean_pdf_text(f"Tel. {client_phone}"), border=0)

    y_after_client = pdf.get_y()
    pdf.set_xy(110, 70)
    pdf.multi_cell(80, 7, clean_pdf_text(technician_name), border=0)
    if technician_phone:
        pdf.set_x(110)
        pdf.set_font("Arial", "", 9)
        pdf.multi_cell(80, 6, clean_pdf_text(f"Tel. {technician_phone}"), border=0)
    pdf.set_y(max(y_after_client, pdf.get_y()) + 8)

    pdf.set_x(20)
    pdf.set_fill_color(241, 245, 249)
    pdf.set_text_color(33, 37, 41)
    pdf.set_font("Arial", "B", 11)
    pdf.cell(110, 10, "Descripcion del servicio", border=1, fill=True)
    pdf.cell(60, 10, "Valor", border=1, ln=True, align="R", fill=True)

    table_y = pdf.get_y()
    pdf.set_x(20)
    pdf.set_font("Arial", "", 10)
    pdf.set_text_color(55, 65, 81)
    pdf.multi_cell(110, 8, clean_pdf_text(work_concept), border=1)
    description_height = max(pdf.get_y() - table_y, 18)

    pdf.set_xy(130, table_y)
    pdf.set_font("Arial", "B", 11)
    pdf.set_text_color(33, 37, 41)
    pdf.cell(60, description_height, money_cop(total_value), border=1, align="R")

    pdf.set_y(table_y + description_height + 8)
    pdf.set_x(20)
    pdf.set_text_color(88, 99, 115)
    pdf.set_font("Arial", "B", 10)
    pdf.cell(42, 8, "Metodo de pago:", border=0)
    pdf.set_font("Arial", "", 10)
    pdf.cell(60, 8, clean_pdf_text(payment_method), border=0)

    pdf.set_x(105)
    pdf.set_fill_color(25, 35, 50)
    pdf.set_text_color(255, 255, 255)
    pdf.set_font("Arial", "B", 13)
    pdf.cell(45, 13, "TOTAL", border=0, fill=True)
    pdf.cell(40, 13, money_cop(total_value), border=0, ln=True, align="R", fill=True)

    pdf.ln(16)
    pdf.set_x(20)
    pdf.set_text_color(88, 99, 115)
    pdf.set_font("Arial", "", 10)
    pdf.multi_cell(
        170,
        6,
        clean_pdf_text(
            "Este documento sirve como soporte del cobro por el servicio descrito. "
            "Pago sujeto a las condiciones acordadas entre cliente y prestador."
        ),
    )

    pdf.ln(18)
    pdf.set_x(20)
    pdf.set_draw_color(140, 150, 165)
    pdf.cell(85, 0, "", border="T")
    pdf.ln(3)
    pdf.set_x(20)
    pdf.set_text_color(33, 37, 41)
    pdf.set_font("Arial", "B", 10)
    pdf.cell(85, 7, clean_pdf_text(technician_name), ln=True, align="C")
    pdf.set_x(20)
    pdf.set_text_color(88, 99, 115)
    pdf.set_font("Arial", "", 9)
    pdf.cell(85, 5, "Firma / Recibido por", ln=True, align="C")

    pdf_output = pdf.output(dest="S")
    if isinstance(pdf_output, str):
        return pdf_output.encode("latin-1")
    return bytes(pdf_output)


if "dark_mode" not in st.session_state:
    st.session_state.dark_mode = False

dark_mode = st.toggle("Modo oscuro", key="dark_mode")

theme_override = (
    """
        [data-testid="stAppViewContainer"] {
            background:
                radial-gradient(circle at top left, rgba(45, 212, 191, 0.16), transparent 30rem),
                radial-gradient(circle at bottom right, rgba(245, 158, 11, 0.12), transparent 28rem),
                #0b1120 !important;
            color: #e5eef6;
        }
        [data-testid="stHeader"] {
            background: rgba(11, 17, 32, 0.88);
        }
        [data-testid="stForm"] {
            background: rgba(15, 23, 42, 0.72);
            border-color: rgba(45, 212, 191, 0.22);
        }
        div[data-testid="stFormSubmitButton"] button,
        div[data-testid="stDownloadButton"] button,
        div[data-testid="stLinkButton"] a {
            background: linear-gradient(135deg, #0f766e, #164e63) !important;
            border: 1px solid rgba(94, 234, 212, 0.42) !important;
            color: #ffffff !important;
            font-weight: 700;
        }
        div[data-testid="stFormSubmitButton"] button *,
        div[data-testid="stDownloadButton"] button *,
        div[data-testid="stLinkButton"] a * {
            color: #ffffff !important;
        }
        div[data-testid="stFormSubmitButton"] button:hover,
        div[data-testid="stDownloadButton"] button:hover,
        div[data-testid="stLinkButton"] a:hover {
            background: linear-gradient(135deg, #14b8a6, #0f766e) !important;
            border-color: #5eead4 !important;
            color: #ffffff !important;
        }
        h1, label, [data-testid="stMarkdownContainer"] p {
            color: #e5eef6;
        }
        .subtitle {
            color: #9fb2c7;
        }
        .receipt-preview {
            border-color: rgba(45, 212, 191, 0.28);
            background: linear-gradient(180deg, #111827 0%, #0f172a 100%);
            color: #e5eef6;
            box-shadow: 0 16px 38px rgba(0, 0, 0, 0.34);
        }
        .receipt-party {
            border-color: rgba(45, 212, 191, 0.24);
            background: rgba(20, 83, 78, 0.24);
        }
        .receipt-party-label,
        .receipt-amount {
            color: #5eead4;
        }
        .receipt-party-name,
        .receipt-table-head {
            color: #e5eef6;
        }
        .receipt-table,
        .receipt-table-row div {
            border-color: rgba(45, 212, 191, 0.24);
        }
        .receipt-table-head {
            background: rgba(15, 118, 110, 0.32);
        }
        .receipt-note {
            color: #b6c6d8;
        }
    """
    if dark_mode
    else """
        [data-testid="stAppViewContainer"] {
            background:
                radial-gradient(circle at top left, rgba(14, 165, 164, 0.12), transparent 30rem),
                radial-gradient(circle at bottom right, rgba(245, 158, 11, 0.10), transparent 28rem),
                #f8fafc !important;
            color: #17313b;
        }
        [data-testid="stHeader"] {
            background: rgba(248, 250, 252, 0.88);
        }
        [data-testid="stForm"] {
            background: rgba(255, 255, 255, 0.82);
            border-color: rgba(15, 118, 110, 0.18);
            box-shadow: 0 16px 38px rgba(15, 23, 42, 0.08);
        }
        h1, label, [data-testid="stMarkdownContainer"] p {
            color: #17313b !important;
        }
        .subtitle {
            color: #527083 !important;
        }
        div[data-baseweb="input"] input,
        div[data-baseweb="textarea"] textarea,
        div[data-baseweb="select"] > div {
            background-color: #ffffff !important;
            color: #17313b !important;
            border-color: #cde9e5 !important;
        }
        div[data-baseweb="input"] input::placeholder,
        div[data-baseweb="textarea"] textarea::placeholder {
            color: #78909c !important;
            opacity: 1 !important;
        }
        div[data-testid="stFormSubmitButton"] button,
        div[data-testid="stDownloadButton"] button,
        div[data-testid="stLinkButton"] a {
            background: linear-gradient(135deg, #0f766e, #164e63) !important;
            border: 1px solid rgba(15, 118, 110, 0.35) !important;
            color: #ffffff !important;
            font-weight: 700;
        }
        div[data-testid="stFormSubmitButton"] button *,
        div[data-testid="stDownloadButton"] button *,
        div[data-testid="stLinkButton"] a * {
            color: #ffffff !important;
        }
        div[data-testid="stFormSubmitButton"] button:hover,
        div[data-testid="stDownloadButton"] button:hover,
        div[data-testid="stLinkButton"] a:hover {
            background: linear-gradient(135deg, #14b8a6, #0f766e) !important;
            border-color: #0f766e !important;
        }
    """
)

st.markdown(
    """
    <style>
        .main .block-container {
            max-width: 760px;
            padding-top: 1.25rem;
            padding-bottom: 2rem;
        }
        [data-testid="stAppViewContainer"] {
            background:
                radial-gradient(circle at top left, rgba(14, 165, 164, 0.12), transparent 30rem),
                radial-gradient(circle at bottom right, rgba(245, 158, 11, 0.10), transparent 28rem),
                var(--background-color);
        }
        h1 {
            font-size: clamp(1.8rem, 5vw, 2.4rem);
            letter-spacing: 0;
        }
        .subtitle {
            color: #64748b;
            font-size: 1rem;
            margin-top: -0.6rem;
            margin-bottom: 1.25rem;
        }
        .receipt-preview {
            border: 1px solid rgba(15, 118, 110, 0.22);
            border-radius: 8px;
            background: linear-gradient(180deg, #ffffff 0%, #fbfdfa 100%);
            color: #17313b;
            overflow: hidden;
            box-shadow: 0 16px 38px rgba(15, 23, 42, 0.14);
        }
        .receipt-preview * {
            color: inherit;
        }
        .receipt-top {
            display: flex;
            justify-content: space-between;
            gap: 1rem;
            background: linear-gradient(135deg, #0f766e 0%, #164e63 72%, #92400e 100%);
            color: #ffffff;
            padding: 1.15rem;
            margin-bottom: 0;
        }
        .receipt-title {
            font-size: 1.25rem;
            font-weight: 700;
        }
        .receipt-muted {
            color: #687385;
            font-size: 0.9rem;
        }
        .receipt-top .receipt-muted,
        .receipt-top .receipt-id {
            color: #d9fffb;
        }
        .receipt-id {
            font-weight: 700;
            text-align: right;
            white-space: nowrap;
        }
        .receipt-body {
            padding: 1.15rem;
        }
        .receipt-parties {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 1rem;
            margin-bottom: 1rem;
        }
        .receipt-party {
            border: 1px solid #cde9e5;
            border-radius: 8px;
            padding: 0.85rem;
            background: #f1fbf8;
        }
        .receipt-party-label {
            color: #0f766e;
            font-size: 0.78rem;
            font-weight: 700;
            margin-bottom: 0.35rem;
            text-transform: uppercase;
        }
        .receipt-party-name {
            color: #17313b;
            font-weight: 700;
        }
        .receipt-table {
            border: 1px solid #cde9e5;
            border-radius: 8px;
            overflow: hidden;
        }
        .receipt-table-head,
        .receipt-table-row {
            display: grid;
            grid-template-columns: 1fr 160px;
        }
        .receipt-table-head {
            background: #e0f2f1;
            color: #134e4a;
            font-weight: 700;
        }
        .receipt-table-head div,
        .receipt-table-row div {
            padding: 0.8rem;
        }
        .receipt-table-row div {
            border-top: 1px solid #cde9e5;
        }
        .receipt-amount {
            text-align: right;
            font-weight: 700;
            color: #0f766e;
        }
        .receipt-row {
            display: grid;
            grid-template-columns: 120px 1fr;
            gap: 0.7rem;
            margin: 0.45rem 0;
        }
        .receipt-label {
            color: #687385;
            font-weight: 600;
        }
        .receipt-total {
            margin-top: 1rem;
            padding: 0.8rem;
            border-radius: 8px;
            background: linear-gradient(135deg, #0f766e, #164e63);
            color: #ffffff;
            display: flex;
            justify-content: space-between;
            font-size: 1.1rem;
            font-weight: 700;
        }
        .receipt-note {
            margin-top: 1rem;
            color: #64748b;
            font-size: 0.88rem;
            line-height: 1.45;
        }
    """
    + theme_override
    + """
        @media (max-width: 520px) {
            .receipt-top {
                display: block;
            }
            .receipt-id {
                margin-top: 0.6rem;
                text-align: left;
            }
            .receipt-parties,
            .receipt-table-head,
            .receipt-table-row {
                grid-template-columns: 1fr;
            }
            .receipt-amount {
                text-align: left;
            }
            .receipt-total {
                display: block;
            }
        }
    </style>
    """,
    unsafe_allow_html=True,
)

st.title("Recibo de cobro")
st.markdown(
    '<p class="subtitle">Crea un recibo rapido y profesional para servicios en Barranquilla.</p>',
    unsafe_allow_html=True,
)

if "technician_name" not in st.session_state:
    st.session_state.technician_name = ""
if "technician_phone" not in st.session_state:
    st.session_state.technician_phone = ""

with st.form("receipt_form"):
    client_name = st.text_input("Nombre del cliente", placeholder="Ej. Carlos Martinez")
    client_phone = st.number_input(
        "Telefono del cliente",
        min_value=0,
        step=1,
        format="%d",
        placeholder="Ej. 3001234567",
    )
    work_concept = st.text_area(
        "Concepto del trabajo",
        placeholder="Ej. Revision y reparacion de lavadora",
        height=110,
    )

    left, right = st.columns(2)
    with left:
        total_value = st.number_input(
            "Valor total",
            min_value=0,
            step=1000,
            format="%d",
            placeholder="Ej. 120000",
        )
    with right:
        receipt_date = st.date_input("Fecha", value=date.today(), format="DD/MM/YYYY")

    payment_method = st.selectbox(
        "Metodo de Pago",
        ["Efectivo", "Nequi", "Daviplata", "Transferencia"],
    )

    technician_left, technician_right = st.columns(2)
    with technician_left:
        technician_name = st.text_input(
            "Nombre del tecnico",
            key="technician_name",
            placeholder="Ej. Luis Gomez",
        )
    with technician_right:
        technician_phone = st.text_input(
            "Telefono del tecnico",
            key="technician_phone",
            placeholder="Ej. 3001234567",
        )

    submitted = st.form_submit_button("Generar Recibo", use_container_width=True)

if submitted:
    missing_fields = []
    if not client_name.strip():
        missing_fields.append("nombre del cliente")
    if client_phone <= 0:
        missing_fields.append("telefono del cliente")
    if not work_concept.strip():
        missing_fields.append("concepto del trabajo")
    if total_value <= 0:
        missing_fields.append("valor total")
    if not technician_name.strip():
        missing_fields.append("nombre del tecnico")
    if not only_digits(technician_phone):
        missing_fields.append("telefono del tecnico")

    if missing_fields:
        st.error("Completa estos campos: " + ", ".join(missing_fields) + ".")
    else:
        client_phone_text = str(int(client_phone))
        technician_phone_text = only_digits(technician_phone)

        pdf_bytes = build_pdf(
            client_name=client_name.strip(),
            client_phone=client_phone_text,
            work_concept=work_concept.strip(),
            total_value=float(total_value),
            receipt_date=receipt_date,
            technician_name=technician_name.strip(),
            technician_phone=technician_phone_text,
            payment_method=payment_method,
        )

        st.success("Recibo generado.")
        st.subheader("Previsualizacion")

        safe_client_name = escape(client_name.strip())
        safe_client_phone = escape(client_phone_text)
        safe_work_concept = escape(work_concept.strip()).replace("\n", "<br>")
        safe_technician_name = escape(technician_name.strip())
        safe_technician_phone = escape(technician_phone_text)
        safe_payment_method = escape(payment_method)
        safe_receipt_id = receipt_number(receipt_date, client_name.strip())

        st.markdown(
            f"""
            <div class="receipt-preview">
                <div class="receipt-top">
                    <div>
                        <div class="receipt-title">RECIBO DE COBRO</div>
                        <div class="receipt-muted">Servicios tecnicos y reparaciones - Barranquilla</div>
                    </div>
                    <div>
                        <div class="receipt-id">{safe_receipt_id}</div>
                        <div class="receipt-muted">{receipt_date.strftime("%d/%m/%Y")}</div>
                    </div>
                </div>
                <div class="receipt-body">
                    <div class="receipt-parties">
                        <div class="receipt-party">
                            <div class="receipt-party-label">Cobrar a</div>
                            <div class="receipt-party-name">{safe_client_name}</div>
                            <div class="receipt-muted">Tel. {safe_client_phone}</div>
                        </div>
                        <div class="receipt-party">
                            <div class="receipt-party-label">Prestador</div>
                            <div class="receipt-party-name">{safe_technician_name}</div>
                            <div class="receipt-muted">Tel. {safe_technician_phone}</div>
                        </div>
                    </div>
                    <div class="receipt-table">
                        <div class="receipt-table-head">
                            <div>Descripcion del servicio</div>
                            <div class="receipt-amount">Valor</div>
                        </div>
                        <div class="receipt-table-row">
                            <div>{safe_work_concept}</div>
                            <div class="receipt-amount">{money_cop(float(total_value))}</div>
                        </div>
                    </div>
                    <div class="receipt-note">
                        Metodo de pago: <strong>{safe_payment_method}</strong>
                    </div>
                    <div class="receipt-total">
                        <span>Total a pagar</span>
                        <span>{money_cop(float(total_value))}</span>
                    </div>
                    <div class="receipt-note">
                        Este documento sirve como soporte del cobro por el servicio descrito.
                        Pago sujeto a las condiciones acordadas entre cliente y prestador.
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        file_name = f"recibo_{receipt_date.strftime('%Y%m%d')}.pdf"
        whatsapp_phone = client_phone_text
        if len(whatsapp_phone) == 10 and whatsapp_phone.startswith("3"):
            whatsapp_phone = "57" + whatsapp_phone
        pdf_link_text = "[link_del_pdf]"
        whatsapp_text = f"Hola, aqu\u00ed te env\u00edo el recibo de tu servicio: {pdf_link_text}"
        whatsapp_url = f"https://wa.me/{whatsapp_phone}?text={quote(whatsapp_text)}"

        col_download, col_whatsapp = st.columns(2)
        with col_download:
            st.download_button(
                "Descargar PDF",
                data=pdf_bytes,
                file_name=file_name,
                mime="application/pdf",
                use_container_width=True,
            )
        with col_whatsapp:
            st.link_button("Compartir por WhatsApp", whatsapp_url, use_container_width=True)
else:
    st.info("Completa el formulario y genera tu recibo cuando este listo.")
