import os
import json
import streamlit as st
import pandas as pd
from rdflib import Graph, URIRef, Literal
from SPARQLWrapper import SPARQLWrapper, JSON
from dotenv import load_dotenv
import google.generativeai as genai
from http.server import SimpleHTTPRequestHandler, HTTPServer
import threading

# Load environment variables from .env file
load_dotenv()

# Configure the Gemini API
api_key = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=api_key)
model = genai.GenerativeModel("gemini-1.5-flash")

# Set page configuration
st.set_page_config(layout="wide")

# Define the SPARQL endpoint
SPARQL_ENDPOINT = "https://dbpedia.org/sparql"

# Sidebar for Filters
with st.sidebar:
    st.header("Filters")
    st.button("Role")
    st.button("Data Type")
    st.button("Layer Depth")
    st.button("Material")
    st.button("Company")

# Function to convert SPARQL results to JSON-LD
def convert_to_jsonld(df):
    graph = Graph()
    for index, row in df.iterrows():
        s = URIRef(row['building'])
        p1 = URIRef("http://www.w3.org/2000/01/rdf-schema#label")
        o1 = Literal(row['name'])
        p2 = URIRef("http://dbpedia.org/ontology/abstract")
        o2 = Literal(row['abstract'])
        graph.add((s, p1, o1))
        graph.add((s, p2, o2))
    return graph.serialize(format='json-ld', indent=4)

# Function to serve JSON-LD data
class JSONHandler(SimpleHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "application/json")
        self.end_headers()
        self.wfile.write(st.session_state['jsonld_data'].encode())

def start_server():
    server = HTTPServer(('localhost', 8000), JSONHandler)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    return server

def stop_server(server):
    server.shutdown()
    server.server_close()

# Initialize session state variables
if 'messages' not in st.session_state:
    st.session_state['messages'] = []

if 'view' not in st.session_state:
    st.session_state['view'] = "Table"

if 'sparql_query' not in st.session_state:
    st.session_state['sparql_query'] = ""

if 'df' not in st.session_state:
    st.session_state['df'] = pd.DataFrame()

if 'jsonld_data' not in st.session_state:
    st.session_state['jsonld_data'] = ""

if 'server' not in st.session_state:
    st.session_state['server'] = None

if 'user_input' not in st.session_state:
    st.session_state['user_input'] = ""

if 'rerun' not in st.session_state:
    st.session_state['rerun'] = False

# Main Layout
# Split layout into top (Graph/Table) and bottom (SPARQL/Chat Query)
top_section, bottom_section = st.container(), st.container()

# Top Section: Graph/Table
with top_section:
    col1, col2 = st.columns([2, 6])  # Adjust column widths as needed
    with col1:
        view = st.radio("View", ["Table", "WebVOWL"], horizontal=True, index=["Table", "WebVOWL"].index(st.session_state['view']))
        st.session_state['view'] = view

    with col2:
        if not st.session_state['df'].empty:
            df = st.session_state['df']
            if view == "Table":
                st.dataframe(df)
            elif view == "WebVOWL":
                if st.session_state['jsonld_data']:
                    if not st.session_state['server']:
                        st.session_state['server'] = start_server()
                    webvowl_url = "http://localhost:3000/?url=http://localhost:8000"
                    st.components.v1.iframe(webvowl_url, height=600, scrolling=True)
                else:
                    st.write("Run a SPARQL query to visualize the data in WebVOWL.")

# Bottom Section: SPARQL/Chat Query
with bottom_section:
    query_type = st.radio("Query Type", ["SPARQL", "Visual Block Builder", "Chat"], horizontal=True)

    if query_type == "SPARQL":
        sparql_query = """PREFIX dbo: <http://dbpedia.org/ontology/>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

SELECT ?building ?name ?abstract
WHERE {
  ?building a dbo:Building ;
           rdfs:label ?name ;
           dbo:abstract ?abstract .
  FILTER (lang(?name) = "en" && lang(?abstract) = "en")
}
LIMIT 10"""
        sparql_query = st.text_area("SPARQL Query", sparql_query, height=300)
        st.session_state['sparql_query'] = sparql_query

        if st.button("Run Query"):
            sparql = SPARQLWrapper(SPARQL_ENDPOINT)
            sparql.setQuery(sparql_query)
            sparql.setReturnFormat(JSON)

            try:
                results = sparql.query().convert()
                columns = results["head"]["vars"]
                data = []

                for result in results["results"]["bindings"]:
                    row = []
                    for col in columns:
                        row.append(result.get(col, {}).get("value", ""))
                    data.append(row)

                df = pd.DataFrame(data, columns=columns)
                st.session_state['df'] = df
                # st.session_state['view'] = "Table"  # Set the view to Table after query execution

                # Convert to JSON-LD and store in session state
                jsonld_data = convert_to_jsonld(df)
                st.session_state['jsonld_data'] = jsonld_data

                # Trigger a rerun by updating session state
                st.session_state['rerun'] = True

            except Exception as e:
                st.error(f"Error running the query: {e}")

    elif query_type == "Visual Block Builder":
        if not st.session_state['df'].empty:
            df = st.session_state['df']
            g = Graph()
            for index, row in df.iterrows():
                if len(row) == 3:
                    s = URIRef(row.iloc[0]) if row.iloc[0].startswith("http") else Literal(row.iloc[0])
                    p = URIRef(row.iloc[1]) if row.iloc[1].startswith("http") else Literal(row.iloc[1])
                    o = URIRef(row.iloc[2]) if row.iloc[2].startswith("http") else Literal(row.iloc[2])
                    g.add((s, p, o))

            st.write("RDF Explorer")
            for s, p, o in g:
                st.write(f"{s} {p} {o}")

    elif query_type == "Chat":
        def send_message():
            user_message = st.session_state['user_input']
            if user_message.strip() != "":
                st.session_state['messages'].append({"role": "user", "content": user_message})
                st.session_state['user_input'] = ""

                # Call Gemini API
                response = model.generate_content(user_message)
                st.session_state['messages'].append({"role": "assistant", "content": response.text})

        st.markdown("<style>.user-message { text-align: right; background-color: #f0f0f0; padding: 10px; border-radius: 10px; } .assistant-message { text-align: left; padding: 10px; border-radius: 10px; }</style>", unsafe_allow_html=True)

        # Display the conversation messages
        for message in st.session_state['messages']:
            if message['role'] == 'user':
                st.markdown(f"<div class='user-message'>{message['content']}</div>", unsafe_allow_html=True)
            else:
                st.markdown(f"<div class='assistant-message'>{message['content']}</div>", unsafe_allow_html=True)

        # Add static suggestion buttons
        static_question_cols = st.columns(5)
        with static_question_cols[0]:
            if st.button("Please explain me this SPARQL Query", key="explain_query"):
                user_message = "Please explain me this SPARQL Query."
                st.session_state['messages'].append({"role": "user", "content": user_message})
                sparql_query = st.session_state.get('sparql_query', '')
                response = model.generate_content(user_message + " Here is the data: " + st.session_state['df'].to_string() + " and the SPARQL query: " + sparql_query)
                st.session_state['messages'].append({"role": "assistant", "content": response.text})
                st.session_state['rerun'] = True

        with static_question_cols[1]:
            if st.button("What are the key insights from this data?", key="key_insights"):
                user_message = "What are the key insights from this data?"
                st.session_state['messages'].append({"role": "user", "content": user_message})
                response = model.generate_content(user_message + " Here is the data: " + st.session_state['df'].to_string())
                st.session_state['messages'].append({"role": "assistant", "content": response.text})
                st.session_state['rerun'] = True

        with static_question_cols[2]:
            if st.button("Can you summarize the data in this table?", key="summarize_data"):
                user_message = "Can you summarize the data in this table?"
                st.session_state['messages'].append({"role": "user", "content": user_message})
                response = model.generate_content(user_message + " Here is the data: " + st.session_state['df'].to_string())
                st.session_state['messages'].append({"role": "assistant", "content": response.text})
                st.session_state['rerun'] = True

        with static_question_cols[3]:
            if st.button("What patterns can you identify in this data?", key="identify_patterns"):
                user_message = "What patterns can you identify in this data?"
                st.session_state['messages'].append({"role": "user", "content": user_message})
                response = model.generate_content(user_message + " Here is the data: " + st.session_state['df'].to_string())
                st.session_state['messages'].append({"role": "assistant", "content": response.text})
                st.session_state['rerun'] = True

        with static_question_cols[4]:
            if st.button("How can I improve this SPARQL query?", key="improve_query"):
                user_message = "How can I improve this SPARQL query?"
                st.session_state['messages'].append({"role": "user", "content": user_message})
                sparql_query = st.session_state.get('sparql_query', '')
                response = model.generate_content(user_message + " Here is the data: " + st.session_state['df'].to_string() + " and the SPARQL query: " + sparql_query)
                st.session_state['messages'].append({"role": "assistant", "content": response.text})
                st.session_state['rerun'] = True

        # Generate dynamic questions based on the SPARQL query
        if 'sparql_query' in st.session_state:
            if 'dynamic_questions' not in st.session_state:
                dynamic_questions_prompt = f"Please generate 5 plain text questions based on the following SPARQL query without any introductory text or special formatting: {st.session_state['sparql_query']}"
                dynamic_response = model.generate_content(dynamic_questions_prompt)
                st.session_state['dynamic_questions'] = [q for q in dynamic_response.text.split('\n') if q.strip() and q.isascii() and not q.lower().startswith("here are")]

            st.markdown("💡Here are 5 questions dynamically generated by an LLM based on the provided SPARQL query:")
            question_cols = st.columns(5)
            for i, question in enumerate(st.session_state['dynamic_questions']):
                with question_cols[i % 5]:
                    if st.button(question, key=f"dynamic_question_{i}"):
                        user_message = question
                        st.session_state['messages'].append({"role": "user", "content": user_message})
                        response = model.generate_content(user_message + " Here is the data: " + st.session_state['df'].to_string())
                        st.session_state['messages'].append({"role": "assistant", "content": response.text})
                        st.session_state['rerun'] = True

        # Move the text input to the bottom
        st.text_input("Message", key="user_input", on_change=send_message, placeholder="Message SparqlGPT", label_visibility="collapsed")

# Check if rerun is needed
if st.session_state.get('rerun', False):
    st.session_state['rerun'] = False
    st.rerun()

# Stop the server when the app is stopped
if 'server' in st.session_state and st.session_state['server']:
    stop_server(st.session_state['server'])