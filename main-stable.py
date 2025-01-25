import streamlit as st
import streamlit_ace as ace
import pandas as pd
import openai
import re
import uuid

from config import AppConfig
from sparql_utils import run_sparql_query, convert_to_jsonld
from server_utils import JSONLDServer
from chat_utils import ChatManager

# Set page configuration
st.set_page_config(layout="wide")

def main():
    st.title("SparqlGPT - A Modular Refactor (SPARQL + Chat)")

    # Set OpenAI API key from Streamlit secrets
    openai.api_key = st.secrets["OPENAI_API_KEY"]

    # Set a default model
    if "openai_model" not in st.session_state:
        st.session_state["openai_model"] = "gpt-3.5-turbo"

    # Initialize chat history
    if "messages" not in st.session_state:
        st.session_state.messages = []

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
LIMIT 100
"""

    if 'apply_query' not in st.session_state:
        st.session_state['apply_query'] = False

    if 'button_key' not in st.session_state:
        st.session_state['button_key'] = None

    top_section, bottom_section = st.container(), st.container()
    with top_section:
        tab1, tab2, tab3 = st.tabs(["Combined View", "Table", "WebVOWL"])

        webvowl_url = "http://localhost:3000/?url=http://localhost:8000"

        if st.session_state['jsonld_data'] and not st.session_state['is_server_running']:
            st.session_state['server'].start_server(st.session_state['jsonld_data'])
            st.session_state['is_server_running'] = True

        with tab1:
            col1, col2 = st.columns([0.5, 0.5])
            with col1:
                st.subheader("Table")
                df = st.session_state['df']
                if not df.empty:
                    st.dataframe(df, height=600)  # Set the height to match WebVOWL
                else:
                    st.write("No data to show yet. Run a SPARQL query first.")

            with col2:
                st.subheader("WebVOWL")
                if st.session_state['jsonld_data']:
                    st.components.v1.iframe(webvowl_url, height=600, scrolling=True)
                else:
                    st.write("Run a SPARQL query to visualize data in WebVOWL.")

        with tab2:
            st.subheader("Table")
            df = st.session_state['df']
            if not df.empty:
                st.dataframe(df, use_container_width=True, height=600)  # Use the full width of the container
            else:
                st.write("No data to show yet. Run a SPARQL query first.")

        with tab3:
            st.subheader("WebVOWL")
            if st.session_state['jsonld_data']:
                st.components.v1.iframe(webvowl_url, height=600, scrolling=True)
            else:
                st.write("Run a SPARQL query to visualize data in WebVOWL.")

    with bottom_section:
        tab1, tab2 = st.tabs(["Chat and Query Editor", "Visual Block Builder"])

        with tab1:
            col_left, col_right = st.columns([1, 1], gap="large")

            with col_left:
                st.subheader("Chat with SparqlGPT")

                # Create a placeholder for chat messages
                chat_placeholder = st.empty()

                # Function to display chat messages
                def display_chat():
                    with chat_placeholder.container():
                        for i, msg in enumerate(st.session_state.messages):
                            with st.chat_message(msg["role"]):
                                st.markdown(msg["content"])
                                # Check if the message contains a SPARQL query
                                if msg["role"] == "assistant":
                                    extracted_sparql_query = extract_sparql_query(msg["content"])
                                    # st.write(f"Extracted SPARQL Query: {extracted_sparql_query}")  # Debugging line
                                    if extracted_sparql_query:
                                        # st.write("Condition 'if extracted_sparql_query:' is True")  # Debugging line
                                        if st.session_state['button_key'] is None:
                                            st.session_state['button_key'] = f"apply_{i}_{msg['role']}_{uuid.uuid4()}"
                                        # st.write(f"Button Key: {st.session_state['button_key']}")  # Debugging line
                                        button_clicked = st.button("Apply this query", key=st.session_state['button_key'])
                                        # st.write(f"Button clicked: {button_clicked}")  # Debugging line
                                        if button_clicked:
                                            # st.write("Button 'Apply this query' clicked")  # Debugging line
                                            prefixes = """PREFIX dbo: <http://dbpedia.org/ontology/>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>\n\n"""
                                            st.session_state["sparql_query"] = prefixes + extracted_sparql_query
                                            st.session_state["apply_query"] = True
                                            st.session_state['button_key'] = None
                                            st.rerun()

                # Function to extract SPARQL query from a message
                def extract_sparql_query(message):
                    match = re.search(r"SELECT.*?WHERE.*?\}", message, re.DOTALL)
                    return match.group(0) if match else None

                # Display conversation history
                display_chat()

                # Apply the query if the button was clicked
                if st.session_state["apply_query"]:
                    # st.write(f"Updated SPARQL Query: {st.session_state['sparql_query']}")  # Debugging line
                    st.session_state["apply_query"] = False

                # Accept user input
                if prompt := st.chat_input("Ask for a SPARQL query or data insights...", key="chat_input_left"):
                    # Add user message to chat history
                    st.session_state.messages.append({"role": "user", "content": prompt})
                    # Reset button key for new query
                    st.session_state['button_key'] = None
                    # Display user message in chat message container
                    display_chat()

                    # Display assistant response in chat message container
                    response = openai.ChatCompletion.create(
                        model=st.session_state["openai_model"],
                        messages=[
                            {"role": "system", "content": f"The current SPARQL query is: {st.session_state['sparql_query']}"},
                            *[
                                {"role": m["role"], "content": m["content"]}
                                for m in st.session_state.messages
                            ]
                        ]
                    )
                    response_text = response.choices[0].message["content"]
                    st.session_state.messages.append({"role": "assistant", "content": response_text})

                    # Update chat display
                    display_chat()

                # Add a button to reset the chat
                if st.button("Reset Chat"):
                    st.session_state.messages = []
                    st.rerun()

            with col_right:
                st.subheader("SPARQL Query Editor")

                # Create a placeholder for the success message
                query_placeholder = st.empty()

                # Use the current query in the session state
                query_to_display = st.session_state["sparql_query"]
                # st.write(f"Query to display in editor: {query_to_display}")  # Debugging line

                ace_editor_content = ace.st_ace(
                    value=query_to_display,
                    language="sparql",
                    theme="twilight",       # Choose your preferred theme (twilight, dracula, etc.)
                    show_gutter=True,
                    wrap=True,
                    auto_update=True,
                    min_lines=15,
                    key=str(uuid.uuid4())  # Ensure a unique key to force re-render
                )

                # Update the session state with the current content of the editor
                st.session_state["sparql_query"] = ace_editor_content

                if st.button("Run Query", key="run_merged_query", on_click=run_query):
                    pass

                # Display the success message in the placeholder
                if 'query_success' in st.session_state and st.session_state['query_success']:
                    query_placeholder.success("SPARQL query ran successfully.")

                # Display the query output below the button in an expansion section
                with st.expander("Query Results"):
                    if not st.session_state['df'].empty:
                        st.dataframe(st.session_state['df'], use_container_width=True)

        with tab2:
            st.subheader("Visual Block Builder")
            st.components.v1.iframe("https://leipert.github.io/vsb/dbpedia/#/workspace", height=800, scrolling=True)

def run_query():
    try:
        df = run_sparql_query(
            st.session_state["sparql_query"],
            AppConfig().sparql_endpoint
        )
        st.session_state["df"] = df
        st.session_state["jsonld_data"] = convert_to_jsonld(df)
        st.session_state['query_success'] = True
    except Exception as e:
        st.session_state['query_success'] = False
        st.error(f"Error running SPARQL: {e}")

if __name__ == "__main__":
    main()