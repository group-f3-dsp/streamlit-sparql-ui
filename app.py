import streamlit as st
import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt

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

# Main Layout
# Split layout into top (Graph/Table) and bottom (SPARQL/Text Query)
top_section, bottom_section = st.container(), st.container()

# Top Section: Graph/Table
with top_section:
    col1, col2 = st.columns([2, 6])  # Adjust column widths as needed
    with col1:
        st.markdown("<h3 style='color: pink;'>Graph / Table</h3>", unsafe_allow_html=True)
        view = st.radio("View", ["Graph", "Table"], horizontal=True)

    with col2:
        if view == "Table":
            # Example table
            data = pd.DataFrame({
                "Column 1": ["Row 1", "Row 2", "Row 3"],
                "Column 2": [10, 20, 30],
                "Column 3": ["A", "B", "C"]
            })
            st.table(data)
        else:
            # Graph Visualization Example
            st.markdown("<h3 style='text-align: center;'>Graph Representation</h3>", unsafe_allow_html=True)
            
            # Create a sample graph
            G = nx.Graph()
            G.add_edges_from([
                ("Person", "Project"),
                ("Project", "Task"),
                ("Task", "Material"),
                ("Material", "Company")
            ])
            
            # Draw the graph using matplotlib
            pos = nx.spring_layout(G)  # Position the nodes
            fig, ax = plt.subplots(figsize=(6, 4))  # Customize figure size
            nx.draw_networkx_nodes(G, pos, node_size=2000, node_color="skyblue", ax=ax)
            nx.draw_networkx_edges(G, pos, width=2, edge_color="gray", ax=ax)
            nx.draw_networkx_labels(G, pos, font_size=12, font_color="black", ax=ax)
            
            st.pyplot(fig)

# Bottom Section: SPARQL/Text Query
with bottom_section:
    st.markdown("<h3 style='color: pink;'>SPARQL and Query Section</h3>", unsafe_allow_html=True)
    
    # Radio buttons to toggle between SPARQL, Visual, and Text query types
    query_type = st.radio("Query Type", ["SPARQL", "Visual", "Text"], horizontal=True)
    
    # Display content dynamically based on query type
    if query_type == "SPARQL":
        st.markdown("### SPARQL Query Editor")
        st.text_area("Edit your SPARQL Query below:", """
        SELECT ?typeUri ?typeLabel
        WHERE {
            ?typeUri rdfs:subClassOf ?type.
            ?type skos:prefLabel ?typeLabel.
            FILTER (LANG(?typeLabel)="en"||LANG(?typeLabel)="")
        }
        """, height=200)
    elif query_type == "Visual":
        st.markdown("### Visual Representation of SPARQL Query")
        # Example graph visualization for SPARQL data
        G = nx.DiGraph()
        G.add_edges_from([
            ("Person", "Project"),
            ("Project", "Task"),
            ("Task", "Material"),
            ("Material", "Company")
        ])
        pos = nx.spring_layout(G)
        fig, ax = plt.subplots(figsize=(6, 4))
        nx.draw(G, pos, with_labels=True, node_color="pink", node_size=3000, font_size=10, font_color="black", ax=ax)
        st.pyplot(fig)
    elif query_type == "Text":
        st.markdown("### Text Query")
        st.text_area("What data would you like?", placeholder="Enter your query here...", height=200)
