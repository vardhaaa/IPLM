import streamlit as st
import pandas as pd
import plotly.express as px

# ----------------- KONFIG HALAMAN -----------------
st.set_page_config(
    page_title="Dashboard IPLM & TGM",
    layout="wide",
    page_icon="🗺️"
)

# ----------------- LOAD DATA -----------------
@st.cache_data
def load_data():

    # Load data utama
    df = pd.read_pickle('bnr/skripsialhamdulillahbnr.pkl')

    # ----------------- HANDLE CLUSTER -----------------
    if 'kategori_kluster' not in df.columns:
        if 'cluster' in df.columns:
            df['kategori_kluster'] = df['cluster'].map({
                1: 'Tinggi',
                0: 'Sedang',
                2: 'Rendah'
            })

    # Label cluster
    if 'cluster' in df.columns:
        df['cluster_label'] = df['cluster'].astype(str)

    return df


# ----------------- LOAD -----------------
try:
    df = load_data()

except FileNotFoundError:
    st.error("File tidak ditemukan! Pastikan file pickle ada di folder.")
    st.stop()

# ----------------- HEADER -----------------
st.title("🗺️ Dashboard Sebaran Literasi Indonesia")

st.markdown("""
Visualisasi **Indeks Pembangunan Literasi Masyarakat (IPLM)** 
dan **Tingkat Kegemaran Membaca (TGM)** berbasis clustering K-Means.
""")

# ----------------- METRIK -----------------
col1, col2, col3 = st.columns(3)

col1.metric("Total Wilayah", len(df))
col2.metric("Rata-rata IPLM", f"{df['iplm'].mean():.2f}")
col3.metric(
    "Rata-rata TGM",
    f"{df['tingkat_kegemaran_membaca'].mean():.2f}"
)

st.divider()

# ----------------- FILTER -----------------
st.sidebar.header("🔍 Filter Data")

cluster_option = st.sidebar.selectbox(
    "Pilih Kluster",
    ["Semua"] + list(df['kategori_kluster'].dropna().unique())
)

# Filter cluster
if cluster_option != "Semua":
    df = df[df['kategori_kluster'] == cluster_option]

# ----------------- CEK KOORDINAT -----------------
missing = df['latitude'].isna().sum()

if missing > 0:
    st.warning(
        f"Ada {missing} data belum memiliki koordinat "
        f"(tidak tampil di peta)."
    )

# ----------------- UKURAN BUBBLE -----------------
df["bubble_size"] = (
    df["iplm"] +
    df["tingkat_kegemaran_membaca"]
) / 2

# ----------------- PETA -----------------
st.subheader("📍 Peta Sebaran Kluster Literasi")

fig = px.scatter_mapbox(
    df.dropna(subset=['latitude', 'longitude']),

    lat="latitude",
    lon="longitude",

    # warna berdasarkan kategori
    color="kategori_kluster",

    # ukuran bubble
    size="bubble_size",

    hover_name="kab_kota",

    hover_data={
        "iplm": ":.2f",
        "tingkat_kegemaran_membaca": ":.2f",
        "kategori_kluster": True,

        # sembunyikan data teknis
        "latitude": False,
        "longitude": False,
        "bubble_size": False,
        "cluster_label": False
    },

    # warna cluster
    color_discrete_map={
        "Tinggi": "green",
        "Sedang": "yellow",
        "Rendah": "red"
    },

    mapbox_style="open-street-map",

    zoom=4,
    center={"lat": -2.5, "lon": 118},

    height=700
)

fig.update_layout(
    margin=dict(r=0, t=0, l=0, b=0),
    legend_title="Kategori Kluster"
)



fig.update_traces(
    hovertemplate=
    "<b>%{hovertext}</b><br><br>" +
    "📚 IPLM: %{customdata[0]:.2f}<br>" +
    "📖 TGM: %{customdata[1]:.2f}<br>" +
    "🏷️ Cluster: %{customdata[2]}<extra></extra>"
)



st.plotly_chart(fig, use_container_width=True)

# ----------------- RINGKASAN CLUSTER -----------------
st.subheader("📊 Ringkasan Cluster")

cluster_summary = df.groupby('kategori_kluster')[
    ['iplm', 'tingkat_kegemaran_membaca']
].mean().round(2)

st.dataframe(
    cluster_summary,
    use_container_width=True
)

# ----------------- DETAIL DATA -----------------
st.subheader("📋 Detail Data")

st.dataframe(
    df[
        [
            'Kab_Kota',
            'IPLM',
            'TGM',
            'Kategori_Kluster'
        ]
    ],
    use_container_width=True,
    hide_index=True
)

# ----------------- DEBUG OPSIONAL -----------------
# with st.expander("🔧 Debug Data"):
#    st.write(df.head())
 #   st.write("Jumlah data tanpa koordinat:", missing)
  #  st.write("Kolom Data:", df.columns)
