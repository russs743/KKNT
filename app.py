import streamlit as st
import pandas as pd
import gspread
from gspread_dataframe import get_as_dataframe, set_with_dataframe
from google.oauth2.service_account import Credentials

# --- KONEKSI KE GOOGLE SHEETS ---
# Menggunakan st.secrets untuk keamanan
scopes = ["https://www.googleapis.com/auth/spreadsheets"]
creds = Credentials.from_service_account_info(
    st.secrets["gcp_service_account"], scopes=scopes
)
client = gspread.authorize(creds)

# --- Tampilan Aplikasi Streamlit ---
st.set_page_config(page_title="Input Data ke Google Sheets", layout="wide")
st.title("📝 Aplikasi Input Data ke Google Sheets")
st.write("Masukkan link Google Sheet dan data balita di bawah ini.")

# --- Input untuk Link & Nama Sheet ---
st.subheader("🎯 Tujuan Spreadsheet")
gsheet_url = st.text_input("URL Google Spreadsheet:", placeholder="Contoh: https://docs.google.com/spreadsheets/d/...")
worksheet_name = st.text_input("Nama Tab/Worksheet:", "Sheet1") # Defaultnya 'Sheet1'

# --- Form Input Data ---
with st.form("input_form", clear_on_submit=True):
    st.subheader("Formulir Data Balita")
    col1, col2 = st.columns(2)
    with col1:
        nama_anak = st.text_input("Nama Anak")
        jenis_kelamin = st.selectbox("Jenis Kelamin", ["Laki-laki", "Perempuan"])
    with col2:
        umur_bulan = st.number_input("Umur (Bulan)", min_value=0, max_value=72, step=1)
        tinggi_badan = st.number_input("Tinggi Badan (cm)", min_value=0.0, step=0.1, format="%.1f")
    
    submitted = st.form_submit_button("💾 Kirim ke Google Sheets")

# --- Logika saat Tombol Ditekan ---
if submitted:
    if not gsheet_url:
        st.warning("URL Google Spreadsheet tidak boleh kosong!", icon="⚠️")
    elif not nama_anak:
        st.warning("Nama Anak tidak boleh kosong!", icon="⚠️")
    else:
        try:
            st.info("Menyambungkan ke Google Sheets...")
            # Buka spreadsheet berdasarkan URL
            spreadsheet = client.open_by_url(gsheet_url)
            # Pilih worksheet (tab)
            worksheet = spreadsheet.worksheet(worksheet_name)
            
            st.info(f"Membaca data dari '{worksheet_name}'...")
            # Baca data yang sudah ada
            existing_data = get_as_dataframe(worksheet, usecols=[0,1,2,3], header=0)
            # Hapus baris yang kosong semua
            existing_data.dropna(how='all', inplace=True)

            # Buat DataFrame untuk data baru
            new_data = pd.DataFrame({
                "Nama Anak": [nama_anak],
                "Jenis Kelamin": [jenis_kelamin],
                "Umur (Bulan)": [umur_bulan],
                "Tinggi Badan (cm)": [tinggi_badan]
            })
            
            # Gabungkan data lama dan baru
            updated_df = pd.concat([existing_data, new_data], ignore_index=True)
            
            st.info("Mengirim data baru...")
            # Tulis kembali seluruh data ke worksheet
            set_with_dataframe(worksheet, updated_df)
            
            st.success(f"Data untuk **{nama_anak}** berhasil dikirim ke Google Sheets! 🎉")

        except gspread.exceptions.SpreadsheetNotFound:
            st.error("Spreadsheet tidak ditemukan! Cek kembali URL dan pastikan kamu sudah share ke email service account.")
        except gspread.exceptions.WorksheetNotFound:
            st.error(f"Tab/Worksheet dengan nama '{worksheet_name}' tidak ditemukan di spreadsheet tersebut.")
        except Exception as e:
            st.error(f"Terjadi kesalahan: {e}")