import streamlit as st 
import pandas as pd

st.title("La mia Gelateria a Livorno")

sabor = st.selectbox("Scegli il tuo fatto oggi", ["Granita Limone", "Granita Limone & Menta", "Granita Anguria", "Granita Mandorle", "Granita Pistacchio", "Granita Cioccolato", "limone", "Limone & Basilico", "Fragola", "Pesca", "Mango", "Soft", "YMN", "Fior di late", "Straccialeta", "Cocco", "Crema", "Caprilli", "Vaniglia", "Mascarpone", "Chesse", "Nocciola", "Arachidi", "Pistacchio", "Caramello", "Meglio della nutella", "Caffè", "Cioccolato", "Fondente", "Brownie", "Liquiritzia"])
klos = st.number_input("Quanti chili hai fatto?", min_value=0.0)

if st.button("Registra"):
    st.success(f"Hai registrato {klos} kg di {sabor}!")
    st.balloons()