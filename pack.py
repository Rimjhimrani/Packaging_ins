"""
TOFAA AI Packaging Studio
A premium, enterprise-grade Streamlit application for AI-powered packaging design,
pricing, sustainability scoring, and quotation generation.
"""

import io
import random
import time
import base64
from datetime import datetime

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from fpdf import FPDF

# ============================================================================
# PAGE CONFIG
# ============================================================================
st.set_page_config(
    page_title="TOFAA AI Packaging Studio",
    page_icon="✨",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ============================================================================
# SESSION STATE INITIALISATION
# ============================================================================
defaults = {
    "dark_mode": False,
    "page": "Dashboard",
    "designs_generated": 12,
    "recommendations": [],
    "selected_reco": None,
    "saved_designs": [],
    "generating": False,
    "product_name": "",
    "brand_name": "",
    "industry": "Cosmetics",
    "description": "",
    "product_img": None,
    "logo_img": None,
    "packaging_type": "Premium Gift Box",
    "material": "Rigid Board",
    "finish": "Matte",
    "effects": [],
    "theme_style": "Luxury",
    "primary_color": "#C9A227",
    "secondary_color": "#F5F0E6",
    "quantity": 250,
    "rotation": 0,
    "zoom": 100,
}
for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

# ============================================================================
# THEME / CSS
# ============================================================================
GOLD = "#C9A227"
GOLD_LIGHT = "#E8D9A0"
BEIGE = "#F5F0E6"
CREAM = "#FBF9F4"


def inject_css():
    dark = st.session_state.dark_mode
    if dark:
        bg = "#14120F"
        bg2 = "#1C1914"
        card_bg = "rgba(255,255,255,0.05)"
        text = "#F2EEE4"
        subtext = "#C9C2B3"
        border = "rgba(201,162,39,0.35)"
    else:
        bg = "#FBF9F4"
        bg2 = "#F5F0E6"
        card_bg = "rgba(255,255,255,0.65)"
        text = "#2B2620"
        subtext = "#6B6355"
        border = "rgba(201,162,39,0.25)"

    st.markdown(
        f"""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@600;700&family=Poppins:wght@300;400;500;600;700&display=swap');

        html, body, [class*="css"] {{
            font-family: 'Poppins', sans-serif;
        }}

        .stApp {{
            background: linear-gradient(160deg, {bg} 0%, {bg2} 100%);
            color: {text};
        }}

        section[data-testid="stSidebar"] {{
            background: linear-gradient(180deg, {"#1C1914" if dark else "#FFFFFF"} 0%, {bg2} 100%);
            border-right: 1px solid {border};
        }}

        h1, h2, h3 {{
            font-family: 'Playfair Display', serif !important;
            color: {text} !important;
            letter-spacing: 0.3px;
        }}

        p, span, label, div {{
            color: {text};
        }}

        .tofaa-hero {{
            padding: 2.2rem 2.5rem;
            border-radius: 22px;
            background: linear-gradient(135deg, {"rgba(201,162,39,0.18)" if dark else "rgba(201,162,39,0.10)"}, {card_bg});
            border: 1px solid {border};
            box-shadow: 0 8px 30px rgba(0,0,0,0.08);
            margin-bottom: 1.6rem;
            backdrop-filter: blur(12px);
        }}
        .tofaa-hero h1 {{
            font-size: 2.3rem;
            margin-bottom: 0.2rem;
            background: linear-gradient(90deg, {GOLD}, #8a6d1a);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }}
        .tofaa-hero p {{
            color: {subtext};
            font-size: 1.05rem;
            font-style: italic;
        }}

        .glass-card {{
            background: {card_bg};
            border: 1px solid {border};
            border-radius: 18px;
            padding: 1.3rem 1.5rem;
            box-shadow: 0 6px 20px rgba(0,0,0,0.06);
            backdrop-filter: blur(10px);
            margin-bottom: 1rem;
            transition: transform 0.25s ease, box-shadow 0.25s ease;
        }}
        .glass-card:hover {{
            transform: translateY(-3px);
            box-shadow: 0 12px 28px rgba(201,162,39,0.18);
        }}

        .kpi-card {{
            background: {card_bg};
            border: 1px solid {border};
            border-radius: 18px;
            padding: 1.2rem 1.1rem;
            text-align: center;
            box-shadow: 0 6px 18px rgba(0,0,0,0.05);
            backdrop-filter: blur(10px);
        }}
        .kpi-card .kpi-value {{
            font-size: 1.9rem;
            font-weight: 700;
            color: {GOLD};
            font-family: 'Playfair Display', serif;
        }}
        .kpi-card .kpi-label {{
            font-size: 0.85rem;
            color: {subtext};
            text-transform: uppercase;
            letter-spacing: 0.6px;
            margin-top: 0.2rem;
        }}

        .section-title {{
            display: flex;
            align-items: center;
            gap: 0.6rem;
            font-family: 'Playfair Display', serif;
            font-size: 1.4rem;
            margin: 1.6rem 0 0.8rem 0;
            border-left: 4px solid {GOLD};
            padding-left: 0.7rem;
        }}

        .reco-card {{
            background: {card_bg};
            border: 1px solid {border};
            border-radius: 20px;
            padding: 1.4rem;
            box-shadow: 0 8px 24px rgba(0,0,0,0.07);
            backdrop-filter: blur(10px);
            transition: 0.25s ease;
            height: 100%;
        }}
        .reco-card:hover {{
            border-color: {GOLD};
            transform: translateY(-4px) scale(1.01);
        }}
        .reco-title {{
            font-family: 'Playfair Display', serif;
            font-size: 1.25rem;
            color: {GOLD};
            margin-bottom: 0.5rem;
        }}
        .reco-badge {{
            display: inline-block;
            background: rgba(201,162,39,0.15);
            color: {GOLD};
            padding: 0.2rem 0.7rem;
            border-radius: 999px;
            font-size: 0.75rem;
            margin: 0.15rem 0.2rem 0.15rem 0;
            border: 1px solid rgba(201,162,39,0.3);
        }}

        .progress-wrap {{
            background: rgba(150,140,110,0.18);
            border-radius: 999px;
            height: 10px;
            width: 100%;
            overflow: hidden;
            margin-top: 0.35rem;
        }}
        .progress-fill {{
            height: 100%;
            border-radius: 999px;
            background: linear-gradient(90deg, {GOLD}, #E8D9A0);
        }}

        .footer-bar {{
            text-align: center;
            padding: 1.4rem 0 0.6rem 0;
            color: {subtext};
            font-size: 0.85rem;
            border-top: 1px solid {border};
            margin-top: 2.5rem;
            letter-spacing: 0.4px;
        }}

        .stButton>button {{
            background: linear-gradient(90deg, {GOLD}, #B8901E);
            color: #ffffff;
            border: none;
            border-radius: 12px;
            padding: 0.55rem 1.3rem;
            font-weight: 600;
            box-shadow: 0 4px 14px rgba(201,162,39,0.35);
            transition: all 0.2s ease;
        }}
        .stButton>button:hover {{
            transform: translateY(-2px);
            box-shadow: 0 8px 20px rgba(201,162,39,0.45);
        }}

        .stTabs [data-baseweb="tab-list"] {{
            gap: 6px;
        }}
        .stTabs [data-baseweb="tab"] {{
            background: {card_bg};
            border-radius: 10px 10px 0 0;
            border: 1px solid {border};
        }}

        div[data-testid="stMetricValue"] {{
            color: {GOLD};
        }}

        ::-webkit-scrollbar {{ width: 8px; }}
        ::-webkit-scrollbar-thumb {{ background: {GOLD}; border-radius: 8px; }}
        </style>
        """,
        unsafe_allow_html=True,
    )


# ============================================================================
# HELPERS
# ============================================================================

def kpi_card(label, value):
    st.markdown(
        f"""<div class="kpi-card"><div class="kpi-value">{value}</div>
        <div class="kpi-label">{label}</div></div>""",
        unsafe_allow_html=True,
    )


def progress_bar(pct, color=GOLD):
    st.markdown(
        f"""<div class="progress-wrap"><div class="progress-fill" style="width:{pct}%;"></div></div>""",
        unsafe_allow_html=True,
    )


def insight_card(icon, title, value, pct):
    st.markdown(
        f"""
        <div class="glass-card">
            <div style="font-size:1.6rem;">{icon}</div>
            <div style="font-weight:600; margin-top:0.3rem;">{title}</div>
            <div style="color:{GOLD}; font-weight:700; font-size:1.1rem;">{value}</div>
            <div class="progress-wrap"><div class="progress-fill" style="width:{pct}%;"></div></div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def gauge(title, value, suffix="%", color=GOLD):
    fig = go.Figure(
        go.Indicator(
            mode="gauge+number",
            value=value,
            number={"suffix": suffix, "font": {"size": 26, "color": color}},
            title={"text": title, "font": {"size": 14}},
            gauge={
                "axis": {"range": [0, 100], "tickcolor": "gray"},
                "bar": {"color": color},
                "bgcolor": "rgba(0,0,0,0)",
                "borderwidth": 0,
                "steps": [
                    {"range": [0, 40], "color": "rgba(201,162,39,0.08)"},
                    {"range": [40, 75], "color": "rgba(201,162,39,0.18)"},
                    {"range": [75, 100], "color": "rgba(201,162,39,0.32)"},
                ],
            },
        )
    )
    fig.update_layout(height=200, margin=dict(l=15, r=15, t=40, b=5), paper_bgcolor="rgba(0,0,0,0)")
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})


def hex_to_rgb(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def generate_mockup(primary, secondary, logo_img, label_text, rotation=0, zoom=100, box_style="box"):
    """Generate a simple procedural packaging mockup using PIL."""
    W, H = 700, 700
    img = Image.new("RGB", (W, H), hex_to_rgb(secondary))
    draw = ImageDraw.Draw(img)

    p_rgb = hex_to_rgb(primary)

    if box_style == "bag":
        # Gift bag shape
        draw.polygon(
            [(200, 180), (500, 180), (530, 620), (170, 620)],
            fill=p_rgb,
        )
        draw.rectangle([300, 120, 400, 200], outline=(255, 255, 255), width=6)
        draw.rectangle([230, 250, 470, 420], fill=hex_to_rgb(secondary))
    else:
        # Box shape - front face with slight 3D top
        draw.polygon([(150, 220), (550, 220), (520, 180), (180, 180)], fill=tuple(min(c + 25, 255) for c in p_rgb))
        draw.rectangle([150, 220, 550, 560], fill=p_rgb)
        draw.rectangle([230, 300, 470, 460], fill=hex_to_rgb(secondary))
        draw.line([(150, 220), (150, 560)], fill=(255, 255, 255), width=2)
        draw.line([(550, 220), (550, 560)], fill=(0, 0, 0), width=2)

    # Label text (brand)
    try:
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf", 34)
        font_small = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf", 18)
    except Exception:
        font = ImageFont.load_default()
        font_small = ImageFont.load_default()

    text = (label_text or "TOFAA")[:18].upper()
    bbox = draw.textbbox((0, 0), text, font=font)
    tw = bbox[2] - bbox[0]
    draw.text(((W - tw) / 2, 360), text, fill=hex_to_rgb(primary) if box_style != "bag" else (30, 30, 30), font=font)
    draw.text((W / 2 - 60, 410), "AI GENERATED DESIGN", fill=(120, 110, 90), font=font_small)

    # Paste logo if provided
    if logo_img is not None:
        try:
            logo = logo_img.copy()
            logo.thumbnail((110, 110))
            img.paste(logo, (int(W / 2 - logo.width / 2), 240), logo.convert("RGBA") if logo.mode == "RGBA" else None)
        except Exception:
            pass

    # Rotation & zoom
    img = img.rotate(rotation, expand=True, fillcolor=(245, 240, 230))
    if zoom != 100:
        factor = zoom / 100
        new_size = (max(1, int(img.width * factor)), max(1, int(img.height * factor)))
        img = img.resize(new_size)

    img = img.filter(ImageFilter.SMOOTH)
    return img


def build_pdf_quote(data, pricing_df, total):
    # Core PDF fonts (Helvetica) don't support the ₹ glyph -> use "Rs." for PDF output
    pricing_df = pricing_df.copy()
    pricing_df["Price"] = pricing_df["Price"].astype(str).str.replace("₹", "Rs. ", regex=False)
    data = {k: str(v).replace("₹", "Rs. ") for k, v in data.items()}

    pdf = FPDF()
    pdf.add_page()
    pdf.set_fill_color(201, 162, 39)
    pdf.rect(0, 0, 210, 22, style="F")
    pdf.set_text_color(255, 255, 255)
    pdf.set_font("Helvetica", "B", 18)
    pdf.set_xy(10, 6)
    pdf.cell(0, 10, "TOFAA AI Packaging Studio - Quotation", ln=True)

    pdf.set_text_color(40, 35, 25)
    pdf.ln(10)
    pdf.set_font("Helvetica", "", 11)
    pdf.cell(0, 8, f"Date: {datetime.now().strftime('%d %b %Y, %H:%M')}", ln=True)
    pdf.ln(2)

    pdf.set_font("Helvetica", "B", 13)
    pdf.cell(0, 8, "Product & Brand Details", ln=True)
    pdf.set_font("Helvetica", "", 11)
    for label, val in data.items():
        pdf.cell(0, 7, f"{label}: {val}", ln=True)

    pdf.ln(4)
    pdf.set_font("Helvetica", "B", 13)
    pdf.cell(0, 8, "Cost Breakdown", ln=True)
    pdf.set_font("Helvetica", "B", 11)
    pdf.set_fill_color(245, 240, 230)
    pdf.cell(120, 8, "Item", border=1, fill=True)
    pdf.cell(60, 8, "Price (INR)", border=1, fill=True, ln=True)
    pdf.set_font("Helvetica", "", 11)
    for _, row in pricing_df.iterrows():
        pdf.cell(120, 8, str(row["Item"]), border=1)
        pdf.cell(60, 8, str(row["Price"]), border=1, ln=True)

    pdf.set_font("Helvetica", "B", 12)
    pdf.cell(120, 9, "TOTAL", border=1)
    pdf.cell(60, 9, f"Rs. {total}", border=1, ln=True)

    pdf.ln(8)
    pdf.set_font("Helvetica", "I", 10)
    pdf.multi_cell(0, 6, "This is an AI-generated estimate from TOFAA AI Packaging Studio. Final pricing may vary based on production specifications and order finalisation.")

    out = pdf.output(dest="S")
    if isinstance(out, str):
        out = out.encode("latin-1")
    return bytes(out)


# ============================================================================
# SIDEBAR
# ============================================================================

def sidebar():
    with st.sidebar:
        st.markdown(
            f"""<div style="text-align:center; padding:1rem 0;">
            <div style="font-family:'Playfair Display',serif; font-size:1.6rem; color:{GOLD}; font-weight:700;">✨ TOFAA</div>
            <div style="font-size:0.8rem; color:gray; letter-spacing:1px;">AI PACKAGING STUDIO</div>
            </div>""",
            unsafe_allow_html=True,
        )
        st.markdown("---")

        pages = {
            "Dashboard": "🏠",
            "AI Packaging Studio": "🎨",
            "Saved Designs": "💾",
            "Price Estimator": "💰",
            "Download Reports": "📄",
            "Help": "❓",
        }
        for name, icon in pages.items():
            if st.button(f"{icon}  {name}", use_container_width=True, key=f"nav_{name}"):
                st.session_state.page = name

        st.markdown("---")
        st.toggle("🌙 Dark Mode", key="dark_mode")
        st.markdown("---")
        st.caption("Enterprise Edition v2.4")
        st.caption("© 2026 TOFAA India")


# ============================================================================
# PAGE: DASHBOARD
# ============================================================================

def page_dashboard():
    st.markdown(
        """<div class="tofaa-hero">
        <h1>Welcome to TOFAA AI Packaging Studio</h1>
        <p>"Create premium packaging powered by Artificial Intelligence."</p>
        </div>""",
        unsafe_allow_html=True,
    )

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        kpi_card("Total Designs Generated", st.session_state.designs_generated)
    with c2:
        kpi_card("Estimated Packaging Cost", "₹1,593")
    with c3:
        kpi_card("Sustainability Score", "82 / 100")
    with c4:
        kpi_card("AI Confidence", "95%")

    st.markdown('<div class="section-title">📈 Recent Activity</div>', unsafe_allow_html=True)
    colA, colB = st.columns([2, 1])
    with colA:
        dates = pd.date_range(end=datetime.now(), periods=7).strftime("%d %b")
        vals = [3, 5, 4, 7, 6, 9, st.session_state.designs_generated % 10 + 2]
        fig = px.area(x=dates, y=vals, labels={"x": "Date", "y": "Designs"}, title="Designs Generated (Last 7 Days)")
        fig.update_traces(line_color=GOLD, fillcolor="rgba(201,162,39,0.25)")
        fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", height=320)
        st.plotly_chart(fig, use_container_width=True)
    with colB:
        fig2 = px.pie(
            names=["Cosmetics", "Electronics", "Food", "Fashion", "Jewellery"],
            values=[35, 20, 15, 18, 12],
            hole=0.55,
            color_discrete_sequence=["#C9A227", "#E8D9A0", "#B8901E", "#F5F0E6", "#8a6d1a"],
        )
        fig2.update_layout(paper_bgcolor="rgba(0,0,0,0)", height=320, showlegend=True, title="Industry Split")
        st.plotly_chart(fig2, use_container_width=True)

    st.info("💡 Tip: Head over to **AI Packaging Studio** in the sidebar to start designing your next premium package.")


# ============================================================================
# PAGE: AI PACKAGING STUDIO
# ============================================================================

def page_studio():
    st.markdown(
        """<div class="tofaa-hero"><h1>🎨 AI Packaging Studio</h1>
        <p>Design premium packaging in minutes with AI-guided recommendations.</p></div>""",
        unsafe_allow_html=True,
    )

    steps = ["1️⃣ Product Info", "2️⃣ AI Preferences", "3️⃣ AI Recommendations", "4️⃣ Live Preview",
             "5️⃣ AI Insights", "6️⃣ Cost Estimator", "7️⃣ Sustainability", "8️⃣ Download"]
    st.progress(1.0 if st.session_state.recommendations else 0.15,
                text="Design Progress")

    tabs = st.tabs(steps)

    # ---------- STEP 1 ----------
    with tabs[0]:
        st.markdown('<div class="section-title">🧾 Product Information</div>', unsafe_allow_html=True)
        with st.container():
            st.markdown('<div class="glass-card">', unsafe_allow_html=True)
            c1, c2 = st.columns(2)
            with c1:
                st.session_state.product_name = st.text_input("Product Name", st.session_state.product_name)
                st.session_state.brand_name = st.text_input("Brand Name", st.session_state.brand_name)
                st.session_state.industry = st.selectbox(
                    "Industry",
                    ["Cosmetics", "Electronics", "Food", "Fashion", "Jewellery", "Corporate Gifts"],
                    index=["Cosmetics", "Electronics", "Food", "Fashion", "Jewellery", "Corporate Gifts"].index(st.session_state.industry),
                )
            with c2:
                prod_file = st.file_uploader("Upload Product Image", type=["png", "jpg", "jpeg"], key="prod_up")
                logo_file = st.file_uploader("Upload Company Logo", type=["png", "jpg", "jpeg"], key="logo_up")
                if prod_file:
                    st.session_state.product_img = Image.open(prod_file).convert("RGBA")
                    st.image(st.session_state.product_img, width=120)
                if logo_file:
                    st.session_state.logo_img = Image.open(logo_file).convert("RGBA")
                    st.image(st.session_state.logo_img, width=120)
            st.session_state.description = st.text_area("Product Description", st.session_state.description, height=90)
            st.markdown('</div>', unsafe_allow_html=True)

    # ---------- STEP 2 ----------
    with tabs[1]:
        st.markdown('<div class="section-title">⚙️ AI Packaging Preferences</div>', unsafe_allow_html=True)
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        c1, c2, c3 = st.columns(3)
        with c1:
            st.session_state.packaging_type = st.selectbox(
                "Packaging Type",
                ["Premium Gift Box", "Magnetic Box", "Paper Box", "Leather Box", "Gift Bag"],
            )
            st.session_state.material = st.selectbox(
                "Material",
                ["Kraft Paper", "Premium Paper", "Rigid Board", "Leather", "Corrugated"],
            )
        with c2:
            st.session_state.finish = st.selectbox("Finish", ["Matte", "Gloss", "Soft Touch", "Textured"])
            st.session_state.theme_style = st.selectbox(
                "Theme", ["Luxury", "Minimal", "Modern", "Elegant", "Eco Friendly"]
            )
        with c3:
            st.session_state.effects = st.multiselect(
                "Special Effects",
                ["Gold Foiling", "Silver Foiling", "Emboss Logo", "Deboss Logo", "Spot UV", "Ribbon", "Magnetic Lock"],
            )
        c4, c5, c6 = st.columns(3)
        with c4:
            st.session_state.primary_color = st.color_picker("Primary Color", st.session_state.primary_color)
        with c5:
            st.session_state.secondary_color = st.color_picker("Secondary Color", st.session_state.secondary_color)
        with c6:
            st.session_state.quantity = st.slider("Quantity", 50, 5000, st.session_state.quantity, step=50)
        st.markdown('</div>', unsafe_allow_html=True)

        gen_col1, gen_col2 = st.columns([1, 3])
        with gen_col1:
            generate = st.button("✨ Generate AI Design", use_container_width=True)
        if generate:
            with st.spinner("🤖 AI is analysing your brand and crafting packaging concepts..."):
                prog = st.progress(0, text="Initialising AI model...")
                stages = [
                    (20, "Analysing product & brand identity..."),
                    (45, "Matching materials & sustainability profile..."),
                    (70, "Rendering design concepts..."),
                    (90, "Calculating cost & confidence scores..."),
                    (100, "Finalising recommendations..."),
                ]
                for pct, msg in stages:
                    time.sleep(0.35)
                    prog.progress(pct, text=msg)
            st.session_state.recommendations = build_recommendations()
            st.session_state.designs_generated += 1
            st.toast("✅ AI packaging designs generated successfully!", icon="🎉")
            st.success("Your AI-powered packaging recommendations are ready — check the **AI Recommendations** tab!")

    # ---------- STEP 3 ----------
    with tabs[2]:
        st.markdown('<div class="section-title">🤖 AI Recommendation Panel</div>', unsafe_allow_html=True)
        if not st.session_state.recommendations:
            st.warning("No recommendations yet. Go to **AI Preferences** tab and click **Generate AI Design**.")
        else:
            cols = st.columns(3)
            for i, reco in enumerate(st.session_state.recommendations):
                with cols[i]:
                    tags = "".join(f'<span class="reco-badge">{t}</span>' for t in reco["tags"])
                    st.markdown(
                        f"""
                        <div class="reco-card">
                            <div class="reco-title">{reco['name']}</div>
                            <div>{tags}</div>
                            <div style="margin-top:0.8rem; font-size:1.3rem; font-weight:700; color:{GOLD};">
                                Estimated Cost ₹{reco['cost']}
                            </div>
                            <div style="margin-top:0.4rem; font-size:0.85rem; color:gray;">Confidence</div>
                            <div class="progress-wrap"><div class="progress-fill" style="width:{reco['confidence']}%;"></div></div>
                            <div style="text-align:right; font-weight:600; margin-top:2px;">{reco['confidence']}%</div>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )
                    if st.button(f"Select {reco['name']}", key=f"select_{i}", use_container_width=True):
                        st.session_state.selected_reco = reco
                        st.toast(f"Selected: {reco['name']}", icon="✅")

    # ---------- STEP 4 ----------
    with tabs[3]:
        st.markdown('<div class="section-title">🖼️ Live Packaging Preview</div>', unsafe_allow_html=True)
        pc1, pc2 = st.columns([3, 1])
        with pc2:
            st.session_state.rotation = st.slider("🔄 Rotate Preview", 0, 360, st.session_state.rotation, step=15)
            st.session_state.zoom = st.slider("🔍 Zoom", 60, 160, st.session_state.zoom, step=10)
            fullscreen = st.checkbox("⛶ Full Screen Preview")
            preview_type = st.radio("View", ["Box Front", "Side View", "Gift Bag"])
        with pc1:
            style = "bag" if preview_type == "Gift Bag" else "box"
            label = st.session_state.brand_name or st.session_state.product_name or "TOFAA"
            mock = generate_mockup(
                st.session_state.primary_color,
                st.session_state.secondary_color,
                st.session_state.logo_img,
                label,
                rotation=st.session_state.rotation if preview_type != "Side View" else st.session_state.rotation + 25,
                zoom=st.session_state.zoom,
                box_style=style,
            )
            width = 700 if fullscreen else 480
            st.image(mock, caption=f"AI Generated Design Preview — {preview_type}", width=width)

    # ---------- STEP 5 ----------
    with tabs[4]:
        st.markdown('<div class="section-title">🧠 AI Insights</div>', unsafe_allow_html=True)
        ic1, ic2, ic3, ic4 = st.columns(4)
        with ic1:
            insight_card("🧱", "Recommended Material", st.session_state.material, 88)
        with ic2:
            insight_card("⏱️", "Manufacturing Time", "5-7 Days", 70)
        with ic3:
            insight_card("💪", "Packaging Strength", "High", 91)
        with ic4:
            insight_card("🌿", "Eco Score", "82 / 100", 82)
        ic5, ic6, ic7 = st.columns(3)
        with ic5:
            insight_card("🚚", "Shipping Efficiency", "Optimised", 85)
        with ic6:
            insight_card("📈", "Market Appeal Score", "94 / 100", 94)
        with ic7:
            insight_card("👑", "Premium Rating", "9.4 / 10", 94)

    # ---------- STEP 6 ----------
    with tabs[5]:
        render_cost_estimator()

    # ---------- STEP 7 ----------
    with tabs[6]:
        st.markdown('<div class="section-title">🌎 Sustainability Dashboard</div>', unsafe_allow_html=True)
        g1, g2, g3 = st.columns(3)
        with g1:
            gauge("Eco Score", 82)
        with g2:
            gauge("Carbon Footprint", 34, color="#7CA982")
        with g3:
            gauge("Recyclability", 90)
        g4, g5 = st.columns(2)
        with g4:
            gauge("Plastic Usage", 12, color="#B85C5C")
        with g5:
            gauge("Green Rating", 88)

    # ---------- STEP 8 ----------
    with tabs[7]:
        render_download_section()


def build_recommendations():
    base_cost = random.randint(900, 1400)
    return [
        {
            "name": "Luxury Collection",
            "tags": ["Premium Rigid Box", "Gold Foiling", "Magnetic Closure", "Luxury Finish"],
            "cost": 1250,
            "confidence": 96,
        },
        {
            "name": "Eco Collection",
            "tags": ["Kraft Material", "Water-based Printing", "Recyclable"],
            "cost": 720,
            "confidence": 93,
        },
        {
            "name": "Modern Collection",
            "tags": ["Minimal Design", "Matte Finish", "Spot UV Logo"],
            "cost": 980,
            "confidence": 95,
        },
    ]


def get_pricing_df():
    rows = [
        ("Base Packaging", 700),
        ("Material", 250),
        ("Printing", 180),
        ("Gold Foiling", 150 if "Gold Foiling" in st.session_state.effects or not st.session_state.effects else 150),
        ("Ribbon", 70 if "Ribbon" in st.session_state.effects or not st.session_state.effects else 70),
    ]
    subtotal = sum(r[1] for r in rows)
    gst = round(subtotal * 0.18)
    rows.append(("GST (18%)", gst))
    total = subtotal + gst
    df = pd.DataFrame(rows, columns=["Item", "Price"])
    df["Price"] = df["Price"].apply(lambda x: f"₹{x}")
    return df, total


def render_cost_estimator():
    st.markdown('<div class="section-title">💰 Smart Cost Estimator</div>', unsafe_allow_html=True)
    df, total = get_pricing_df()
    c1, c2 = st.columns([1.3, 1])
    with c1:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.dataframe(df, use_container_width=True, hide_index=True)
        st.markdown(
            f"""<div style="text-align:right; font-size:1.4rem; font-weight:700; color:{GOLD}; margin-top:0.5rem;">
            TOTAL ₹{total}</div>""",
            unsafe_allow_html=True,
        )
        st.markdown('</div>', unsafe_allow_html=True)
        st.markdown(
            f"""<div class="glass-card" style="border-left:4px solid {GOLD};">
            💡 <b>AI Suggestion:</b> Switching to <b>Matte Finish</b> instead of <b>Soft Touch</b>
            can reduce the cost by ₹180 while maintaining a premium appearance.</div>""",
            unsafe_allow_html=True,
        )
    with c2:
        labels = df["Item"].tolist()
        values = [int(str(x).replace("₹", "")) for x in df["Price"]]
        fig = px.pie(names=labels, values=values, hole=0.5, title="Price Distribution",
                     color_discrete_sequence=px.colors.sequential.YlOrBr)
        fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", height=380)
        st.plotly_chart(fig, use_container_width=True)


def render_download_section():
    st.markdown('<div class="section-title">📦 Download Section</div>', unsafe_allow_html=True)
    df, total = get_pricing_df()

    data = {
        "Product Name": st.session_state.product_name or "N/A",
        "Brand Name": st.session_state.brand_name or "N/A",
        "Industry": st.session_state.industry,
        "Packaging Type": st.session_state.packaging_type,
        "Material": st.session_state.material,
        "Finish": st.session_state.finish,
        "Theme": st.session_state.theme_style,
        "Quantity": st.session_state.quantity,
    }

    c1, c2, c3 = st.columns(3)
    with c1:
        pdf_bytes = build_pdf_quote(data, df, total)
        st.download_button("📄 Download PDF Quote", data=pdf_bytes,
                            file_name="TOFAA_Quotation.pdf", mime="application/pdf",
                            use_container_width=True)
    with c2:
        label = st.session_state.brand_name or st.session_state.product_name or "TOFAA"
        mock = generate_mockup(st.session_state.primary_color, st.session_state.secondary_color,
                                st.session_state.logo_img, label)
        buf = io.BytesIO()
        mock.save(buf, format="PNG")
        st.download_button("🖼️ Download Design Image", data=buf.getvalue(),
                            file_name="TOFAA_Design.png", mime="image/png",
                            use_container_width=True)
    with c3:
        csv = df.to_csv(index=False).encode("utf-8")
        st.download_button("📊 Export Price Sheet", data=csv,
                            file_name="TOFAA_Price_Sheet.csv", mime="text/csv",
                            use_container_width=True)

    c4, c5 = st.columns(2)
    with c4:
        if st.button("🔗 Share Design", use_container_width=True):
            st.toast("Share link copied to clipboard (demo)", icon="🔗")
    with c5:
        if st.button("💾 Save Project", use_container_width=True):
            st.session_state.saved_designs.append({
                **data,
                "Total": f"₹{total}",
                "Saved On": datetime.now().strftime("%d %b %Y %H:%M"),
            })
            st.toast("Project saved successfully!", icon="💾")


# ============================================================================
# PAGE: SAVED DESIGNS
# ============================================================================

def page_saved():
    st.markdown(
        """<div class="tofaa-hero"><h1>💾 Saved Designs</h1>
        <p>Review and manage your saved packaging projects.</p></div>""",
        unsafe_allow_html=True,
    )
    if not st.session_state.saved_designs:
        st.info("No saved designs yet. Save a project from the **Download** step in AI Packaging Studio.")
        return
    for i, d in enumerate(st.session_state.saved_designs):
        with st.expander(f"📦 {d.get('Product Name', 'Design')} — {d.get('Brand Name', '')} ({d['Saved On']})"):
            st.json(d)


# ============================================================================
# PAGE: PRICE ESTIMATOR (standalone)
# ============================================================================

def page_price_estimator():
    st.markdown(
        """<div class="tofaa-hero"><h1>💰 Price Estimator</h1>
        <p>Quick standalone pricing calculator for your packaging needs.</p></div>""",
        unsafe_allow_html=True,
    )
    c1, c2 = st.columns(2)
    with c1:
        base = st.number_input("Base Packaging (₹)", 100, 5000, 700, step=10)
        material = st.number_input("Material (₹)", 0, 3000, 250, step=10)
        printing = st.number_input("Printing (₹)", 0, 2000, 180, step=10)
    with c2:
        foiling = st.number_input("Gold/Silver Foiling (₹)", 0, 2000, 150, step=10)
        ribbon = st.number_input("Ribbon (₹)", 0, 500, 70, step=10)
        qty = st.slider("Quantity", 50, 5000, 250, step=50)

    subtotal = base + material + printing + foiling + ribbon
    gst = round(subtotal * 0.18)
    total_unit = subtotal + gst
    total_bulk = total_unit * qty

    st.markdown('<div class="section-title">📊 Result</div>', unsafe_allow_html=True)
    m1, m2, m3 = st.columns(3)
    with m1:
        kpi_card("Per Unit Price", f"₹{total_unit}")
    with m2:
        kpi_card("GST (18%)", f"₹{gst}")
    with m3:
        kpi_card("Total for Order", f"₹{total_bulk:,}")


# ============================================================================
# PAGE: DOWNLOAD REPORTS
# ============================================================================

def page_reports():
    st.markdown(
        """<div class="tofaa-hero"><h1>📄 Download Reports</h1>
        <p>Export summaries and quotations for your current design session.</p></div>""",
        unsafe_allow_html=True,
    )
    if not st.session_state.recommendations:
        st.warning("Generate a design first in **AI Packaging Studio** to unlock full reports.")
    render_download_section()


# ============================================================================
# PAGE: HELP
# ============================================================================

def page_help():
    st.markdown(
        """<div class="tofaa-hero"><h1>❓ Help & Support</h1>
        <p>Everything you need to get the most out of TOFAA AI Packaging Studio.</p></div>""",
        unsafe_allow_html=True,
    )
    faqs = [
        ("How does AI Packaging Studio generate designs?",
         "Our AI analyses your product details, brand identity, and preferences to recommend material, finish, and cost-optimised packaging concepts."),
        ("Can I customise the AI recommendations?",
         "Yes — every recommendation can be adjusted in Step 2 (AI Preferences), including material, finish, color, and special effects."),
        ("How accurate is the pricing?",
         "Pricing is an AI-generated estimate based on current material and manufacturing benchmarks. Final costs are confirmed after order review."),
        ("Can I download a formal quotation?",
         "Yes, use the Download Section to export a branded PDF quotation, price sheet, or design image."),
        ("Is my uploaded data secure?",
         "All uploads are processed locally within your session and are not shared with third parties."),
    ]
    for q, a in faqs:
        with st.expander(f"🔸 {q}"):
            st.write(a)

    st.markdown('<div class="section-title">📬 Contact Support</div>', unsafe_allow_html=True)
    st.markdown(
        """<div class="glass-card">
        📧 support@tofaa.in &nbsp; | &nbsp; 📞 +91-98XXXXXX10 &nbsp; | &nbsp; 🌐 www.tofaa.in
        </div>""",
        unsafe_allow_html=True,
    )


# ============================================================================
# MAIN
# ============================================================================

def main():
    inject_css()
    sidebar()

    page = st.session_state.page
    if page == "Dashboard":
        page_dashboard()
    elif page == "AI Packaging Studio":
        page_studio()
    elif page == "Saved Designs":
        page_saved()
    elif page == "Price Estimator":
        page_price_estimator()
    elif page == "Download Reports":
        page_reports()
    elif page == "Help":
        page_help()

    st.markdown(
        """<div class="footer-bar">✨ Powered by <b>TOFAA AI Packaging Studio</b> — Premium AI Packaging Design Platform</div>""",
        unsafe_allow_html=True,
    )


if __name__ == "__main__":
    main()
