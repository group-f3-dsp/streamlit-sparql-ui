import streamlit as st
import pandas as pd

from config import AppConfig
from sparql_utils import run_sparql_query, convert_to_jsonld
from server_utils import JSONLDServer
from chat_utils import ChatManager

def main():
    config = AppConfig()
    chat_manager = ChatManager()

    if 'df' not in st.session_state:
        st.session_state['df'] = pd.DataFrame()

    if 'jsonld_data' not in st.session_state:
        st.session_state['jsonld_data'] = ""

    if 'server' not in st.session_state:
        st.session_state['server'] = JSONLDServer()

    if 'is_server_running' not in st.session_state:
        st.session_state['is_server_running'] = False

    if 'sparql_query' not in st.session_state:
        st.session_state['sparql_query'] = """PREFIX dbo: <http://dbpedia.org/ontology/>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

SELECT ?building ?name ?abstract
WHERE {
  ?building a dbo:Building ;
           rdfs:label ?name ;
           dbo:abstract ?abstract .
  FILTER (lang(?name) = "en" && lang(?abstract) = "en")
}
LIMIT 10
"""

    if 'proposed_query' not in st.session_state:
        st.session_state['proposed_query'] = ""

    st.set_page_config(layout="wide")
    st.title("SparqlGPT - A Modular Refactor (SPARQL + Chat)")

    top_section, bottom_section = st.container(), st.container()
    with top_section:
        col1, col2 = st.columns([2, 6])
        with col1:
            if 'view' not in st.session_state:
                st.session_state['view'] = "Table"
            view = st.radio(
                "View",
                ["Table", "WebVOWL"],
                horizontal=True,
                index=["Table", "WebVOWL"].index(st.session_state['view'])
            )
            st.session_state['view'] = view

        with col2:
            df = st.session_state['df']
            if not df.empty:
                if view == "Table":
                    st.dataframe(df)
                else:
                    if st.session_state['jsonld_data']:
                        if not st.session_state['is_server_running']:
                            st.session_state['server'].start_server(st.session_state['jsonld_data'])
                            st.session_state['is_server_running'] = True
                        webvowl_url = "http://localhost:3000/?url=http://localhost:8000"
                        st.components.v1.iframe(webvowl_url, height=600, scrolling=True)
                    else:
                        st.write("Run a SPARQL query to visualize data in WebVOWL.")
            else:
                st.write("No data to show yet. Run a SPARQL query first.")
    with bottom_section:
        query_type = st.radio(
            "Query Type",
            ["SPARQL + Chat", "Visual Block Builder"],
            horizontal=True,
        )

        if query_type == "SPARQL + Chat":
        
        
            col_left, col_right = st.columns([1.3, 1], gap="large")

            with col_left:
                st.subheader("Chat with SparqlGPT")

                conversation = chat_manager.get_conversation()
                st.markdown(
                    """
                    <style>
                    .user-message {
                        text-align: right; 
                        background-color: #f0f0f0; 
                        padding: 10px; 
                        border-radius: 10px; 
                        margin-bottom: 10px;
                    }
                    .assistant-message {
                        text-align: left; 
                        background-color: #e0f7fa; 
                        padding: 10px; 
                        border-radius: 10px; 
                        margin-bottom: 10px;
                    }
                    </style>
                    """,
                    unsafe_allow_html=True
                )
                for msg in conversation:
                    if msg["role"] == "user":
                        st.markdown(f"<div class='user-message'>{msg['content']}</div>", unsafe_allow_html=True)
                    else:
                        st.markdown(f"<div class='assistant-message'>{msg['content']}</div>", unsafe_allow_html=True)

                if st.session_state["proposed_query"]:
                    st.info(f"Assistant suggested this SPARQL:\n\n{st.session_state['proposed_query']}")
                    if st.button("Use This Query", key="use_ai_query"):
                        st.session_state["sparql_query"] = st.session_state["proposed_query"]
                        st.session_state["proposed_query"] = ""

                def handle_chat_input():
                    user_text = st.session_state["chat_input"]
                    if user_text.strip():
                        chat_manager.add_user_message(user_text)
                        st.session_state["chat_input"] = ""

                        response_text = chat_manager.generate_response(user_text)
                        chat_manager.add_assistant_message(response_text)

                        extracted_query = chat_manager.extract_sparql_query(response_text)
                        st.session_state["proposed_query"] = extracted_query

                st.text_input(
                    "Your message",
                    key="chat_input",
                    on_change=handle_chat_input,
                    placeholder="Ask for a SPARQL query or data insights..."
                )

            with col_right:
                st.subheader("SPARQL Editor")
                st.session_state["sparql_query"] = st.text_area(
                    "Edit your SPARQL query here:",
                    value=st.session_state["sparql_query"],
                    height=250
                )

                if st.button("Run Query", key="run_merged_query"):
                    try:
                        df = run_sparql_query(
                            st.session_state["sparql_query"],
                            config.sparql_endpoint
                        )
                        st.session_state["df"] = df
                        st.success("SPARQL query ran successfully.")
                        st.session_state["jsonld_data"] = convert_to_jsonld(df)
                    except Exception as e:
                        st.error(f"Error running SPARQL: {e}")

                if not st.session_state["df"].empty:
                    st.write("### Query Results:")
                    st.dataframe(st.session_state["df"])

        elif query_type == "Visual Block Builder":
            df = st.session_state['df']
            if not df.empty:
                st.write("RDF Explorer")
                for _, row in df.iterrows():
                    st.write(row.to_dict())
            else:
                st.warning("No data available. Run a SPARQL query first.")

if __name__ == "__main__":
    main()
