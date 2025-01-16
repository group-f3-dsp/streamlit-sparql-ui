import streamlit as st

# Set page configuration
st.set_page_config(layout="wide")

# Sidebar for Filters
with st.sidebar:
    st.header("Filters")
    st.button("Role")
    st.button("Data Type")
    st.button("Layer Depth")
    st.button("Material")
    st.button("Company")

# Main UI
st.markdown("<h1 style='color: pink; text-align: center;'>Graph / Table</h1>", unsafe_allow_html=True)

# Graph/Table toggle
col1, col2 = st.columns(2)
with col1:
    st.radio("View", ["Graph", "Table"], horizontal=True)

# Table placeholder
st.markdown(
    "<div style='border: 2px solid black; padding: 20px; background-color: white;'>"
    "<h3 style='text-align: center;'>Table Placeholder</h3></div>",
    unsafe_allow_html=True
)

# SPARQL Query Section
st.markdown("<h2 style='color: pink;'>SPARQL Query</h2>", unsafe_allow_html=True)
sparql_col1, sparql_col2 = st.columns(2)
with sparql_col1:
    st.radio("SPARQL", ["SPARQL", "Visual", "Text"], horizontal=True)
with sparql_col2:
    st.code("""
    SELECT ?typeUri ?typeLabel
    WHERE {
        ?typeUri rdfs:subClassOf ?type.
        ?type skos:prefLabel ?typeLabel.
        FILTER (LANG(?typeLabel)="en"||LANG(?typeLabel)="")
    }
    """, language="sql")
