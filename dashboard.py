# Import Library
import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import plotly.express as px
import os


# Memastikan Dataset Tersedia Sebelum Dibaca
file_path = os.path.join(os.getcwd(), "data", "day.csv")
if not os.path.exists(file_path):
    st.error("ERROR: File `data/day.csv` tidak ditemukan! Periksa nama folder dan file.")
    st.stop()

day_df = pd.read_csv(file_path)

# Preprocessing Data
day_df["dteday"] = pd.to_datetime(day_df["dteday"])
day_df["is_weekend"] = day_df["weekday"].apply(lambda x: 1 if x in [0, 6] else 0)

# Dashboard Utama
st.title("Bike Sharing Data Dashboard")
st.markdown("### Analisis Peminjaman Sepeda Berdasarkan Musim dan Hari")

# Sidebar - Data filtering
st.sidebar.header("Filter Data")

#Filter Rentang Tanggal
start_date, end_date = st.sidebar.date_input(
    "Pilih Rentang Tanggal",
    [day_df["dteday"].min(), day_df["dteday"].max()],
    min_value=day_df["dteday"].min(),
    max_value=day_df["dteday"].max(),
)

#Filter Rentang Jumlah Peminjaman
min_rentals, max_rentals = st.sidebar.slider(
    "Rentang Jumlah Peminjaman",
    int(day_df["cnt"].min()), int(day_df["cnt"].max()), (100, 5000)
)

#Filter Data Berdasarkan Musim 
season_options = [0, 1, 2, 3, 4]  # 0 sebagai opsi untuk semua musim
selected_season = st.sidebar.selectbox(
    "Pilih Musim:", season_options, format_func=lambda x: "Semua Musim" if x == 0 else ["Semi", "Panas", "Gugur", "Dingin"][x-1]
)

#Filter Data Sesuai Input user
filtered_df = day_df[
    (day_df["dteday"].between(pd.to_datetime(start_date), pd.to_datetime(end_date))) &
    (day_df["cnt"].between(min_rentals, max_rentals))
]

if selected_season != 0:  # Jika bukan "Semua Musim", filter musim
    filtered_df = filtered_df[filtered_df["season"] == selected_season]


# Tampilkan Data Sample
if st.sidebar.checkbox("Tampilkan Sample Data"):
    st.subheader("Sample Data yang Dipilih")
    st.write(filtered_df.head())


# Statistik Peminjaman Sepeda
st.subheader("Statistik Peminjaman Sepeda")

#Rata-rata peminjaman per musim
season_avg = filtered_df.groupby("season")["cnt"].mean().reset_index()
season_avg.columns = ["Season", "Average Rentals"]
st.write("**Rata-rata peminjaman sepeda per musim:**", season_avg)

#Rata-rata peminjaman di hari kerja vs akhir pekan
weekend_avg = filtered_df.groupby("is_weekend")["cnt"].mean().reset_index()
weekend_avg.columns = ["Is Weekend", "Average Rentals"]
st.write("**Rata-rata peminjaman di hari kerja vs akhir pekan:**", weekend_avg)

# Visualisasi 1: Peminjaman Sepeda per Musim (Bar Chart)

st.subheader("Rata-rata Peminjaman Sepeda per Musim")
fig, ax = plt.subplots(figsize=(8, 5))
sns.barplot(x="Season", y="Average Rentals", hue="Season", data=season_avg, ax=ax, palette="viridis", legend=False)
ax.set_title("Rata-rata Peminjaman Sepeda per Musim")
ax.set_xlabel("Musim (1: Semi, 2: Panas, 3: Gugur, 4: Dingin)")
ax.set_ylabel("Jumlah Peminjaman")
st.pyplot(fig)


# Visualisasi 2: Peminjaman Sepeda - Hari Kerja vs Akhir Pekan
st.subheader("Peminjaman Sepeda: Hari Kerja vs Akhir Pekan per Musim")
season_weekend_group = filtered_df.groupby(["season", "is_weekend"])["cnt"].mean().unstack()

fig, ax = plt.subplots(figsize=(8, 5))
season_weekend_group.plot(kind="bar", ax=ax, colormap="coolwarm")
ax.set_title("Rata-rata Peminjaman Sepeda per Musim (Hari Kerja vs Akhir Pekan)")
ax.set_xlabel("Musim (1: Semi, 2: Panas, 3: Gugur, 4: Dingin)")
ax.set_ylabel("Jumlah Peminjaman")
ax.legend(["Hari Kerja", "Akhir Pekan"])
st.pyplot(fig)

# Visualisasi 3: Tren Peminjaman Sepeda Harian
st.subheader("Jumlah Peminjaman Sepeda Harian")
fig = px.line(filtered_df, x="dteday", y="cnt", title="Tren Peminjaman Sepeda Harian", labels={"cnt": "Jumlah Peminjaman", "dteday": "Tanggal"})
st.plotly_chart(fig)
