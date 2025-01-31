import streamlit as st
import streamlit_ace as ace
import pandas as pd
import openai
import re
import uuid

from config import AppConfig
from sparql_utils import run_sparql_query
# from server_utils import JSONLDServer  # Commented out as it's no longer needed
from chat_utils import ChatManager
from endpoints import SPARQL_ENDPOINTS

# Set page configuration
st.set_page_config(layout="wide")

def main():
    # Inject custom CSS to remove top padding
    st.markdown(
        """
        <style>
        /* Remove top padding and margin from the specific st-emotion-cache class */
        .st-emotion-cache-3a3u1y {
            padding-top: 0 !important;  /* Remove top padding */
            margin-top: 0 !important;   /* Remove top margin */
        }

        /* Optionally reset any top margin for the main container */
        .stMainBlockContainer {
            padding-top: 0 !important;  /* Remove top padding */
            margin-top: 0 !important;   /* Remove top margin */
        }

        /* Optional: Reset top margin for the entire app */
        .stApp {
            margin-top: 0 !important;  /* Remove top margin for the app */
        }
        h1 {
            padding-top: 0 !important;
            font-size: 30px !important;
        }

        /* Add margin and padding to the top of the SPARQL Ace editor box */
        .ace_editor {
            margin-top: 0 !important;
            padding-top: 0 !important;
        }

        /* Remove space between the editor box and the subheader */
        .stSubheader {
            margin-bottom: 0 !important;
        }
        </style>
        """,
        unsafe_allow_html=True
    )
    st.markdown("""
        <style>
            #MainMenu, header, footer {visibility: hidden;}

            /* This code gets the first element on the sidebar,
            and overrides its default styling */
            section[data-testid="stSidebar"] div:first-child {
                top: 0;
                height: 0vh;
            }
        </style>
        """,unsafe_allow_html=True)


    # Now you can add your title without extra padding above it
    st.title("SparqlGPT - A Modular Refactor")

    # Set OpenAI API key from Streamlit secrets
    openai.api_key = st.secrets["OPENAI_API_KEY"]

    # Set a default model
    if "openai_model" not in st.session_state:
        st.session_state["openai_model"] = "gpt-3.5-turbo"

    # Initialize chat history
    if "messages" not in st.session_state:
        st.session_state.messages = [{"role": "assistant", "content": "Hello! How can I assist you today?"}]

    config = AppConfig()
    chat_manager = ChatManager()

    if 'df' not in st.session_state:
        st.session_state['df'] = pd.DataFrame()

    # if 'jsonld_data' not in st.session_state:  # Commented out as it's no longer needed
    #     st.session_state['jsonld_data'] = ""

    # if 'server' not in st.session_state:  # Commented out as it's no longer needed
    #     st.session_state['server'] = JSONLDServer()

    # if 'is_server_running' not in st.session_state:  # Commented out as it's no longer needed
    #     st.session_state['is_server_running'] = False

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

    if 'query_executed' not in st.session_state:
        st.session_state['query_executed'] = False

    top_section, bottom_section = st.container(), st.container()
    with top_section:
        tab1, tab2, tab3 = st.tabs(["Combined View", "Table", "WebVOWL"])

        # webvowl_url = "https://service.tib.eu/webvowl"
        webvowl_url = "localhost:8080/webvowl"


        with tab1:
            col1, col2 = st.columns([0.5, 0.5])
            with col1:
                st.subheader("Table")
                df = st.session_state['df']
                if not df.empty:
                    column_config = {}
                    for column in df.columns:
                        # Check if the column contains URLs starting with "http"
                        if df[column].apply(lambda x: isinstance(x, str) and x.startswith("http")).any():
                            column_config[column] = st.column_config.LinkColumn(
                                column,
                                help=f"Links in the {column} column"
                            )

                    # Display the DataFrame with clickable links using st.data_editor
                    if not df.empty:
                        st.data_editor(
                            df,
                            column_config=column_config,
                            hide_index=False,
                            height=400,
                            key="data_editor_1"  # Unique key for this table


                        )
                    else:
                        st.write("No data to show yet. Run a SPARQL query first.")

            with col2:
                st.subheader("WebVOWL")
                st.components.v1.iframe(webvowl_url, height=400, scrolling=True)

        with tab2:
            st.subheader("Table")
            if not df.empty:
                    column_config = {}
                    for column in df.columns:
                        # Check if the column contains URLs starting with "http"
                        if df[column].apply(lambda x: isinstance(x, str) and x.startswith("http")).any():
                            column_config[column] = st.column_config.LinkColumn(
                                column,
                                help=f"Links in the {column} column"
                            )

                    # Display the DataFrame with clickable links using st.data_editor
                    if not df.empty:
                        st.data_editor(
                            df,
                            column_config=column_config,
                            hide_index=False,
                            key="data_editor_2",  # Unique key for this table
                            use_container_width=True  # Make it take up the whole page width


                        )
                    else:
                        st.write("No data to show yet. Run a SPARQL query first.")


        with tab3:
            st.subheader("WebVOWL")
            st.components.v1.iframe(webvowl_url, height=600, scrolling=True)

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
                        with st.container(height=400, border=None,):
                            for i, msg in enumerate(st.session_state.messages):
                                with st.chat_message(msg["role"]):
                                    st.markdown(msg["content"])
                                    # Check if the message contains a SPARQL query and is the last message
                                    if msg["role"] == "assistant" and i == len(st.session_state.messages) - 1:
                                        extracted_sparql_query, extracted_prefixes = extract_sparql_query_and_prefixes(msg["content"])
                                        if extracted_sparql_query:
                                            if st.session_state['button_key'] is None:
                                                st.session_state['button_key'] = f"apply_{i}_{msg['role']}_{uuid.uuid4()}"
                                            button_clicked = st.button("Apply this query", key=st.session_state['button_key'])
                                            if button_clicked:
                                                st.session_state["sparql_query"] = extracted_prefixes + "\n\n" + extracted_sparql_query
                                                st.session_state["apply_query"] = True
                                                st.session_state['button_key'] = None
                                                st.session_state['query_executed'] = False
                                                st.session_state['ace_editor_content'] = st.session_state["sparql_query"]
                                                st.session_state['update_ace_editor'] = True
                                                st.session_state['reload'] = True
                                                st.experimental_set_query_params(reload=st.session_state['reload'])

                # Function to extract SPARQL query and prefixes from a message
                def extract_sparql_query_and_prefixes(message):
                    prefixes = re.findall(r"PREFIX\s+\w+:\s+<[^>]+>", message)
                    query = re.search(r"SELECT.*?WHERE\s*\{.*?\}\s*(LIMIT\s*\d+)?", message, re.DOTALL)
                    return query.group(0) if query else None, "\n".join(prefixes)

                # Display conversation history
                display_chat()

                # Apply the query if the button was clicked
                if st.session_state["apply_query"]:
                    # st.write(f"Updated SPARQL Query: {st.session_state['sparql_query']}")  # Debugging line
                    st.session_state["apply_query"] = False

                # # Reload the page if needed
                # if st.session_state.get('reload', False):
                #     st.session_state['reload'] = False
                #     st.experimental_set_query_params(reload=st.session_state['reload'])

                # Accept user input
                if prompt := st.chat_input("Ask for a SPARQL query in the code block format or data insights...", key="chat_input_left"):
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
                            {"role": "system", "content": f"The current SPARQL endpoint is: {st.session_state['sparql_endpoint']}"},
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
                st.markdown("""
                    <style>.element-container:has(#button) + div button {
                        background-color: #dc3545 !important;
                        color: white !important;
                    }</style>""", unsafe_allow_html=True)

                st.markdown('<span id="button"></span>', unsafe_allow_html=True)
                if st.button("Reset Chat" , key="red", type="primary"):
                    st.experimental_set_query_params(reload=True)
                    st.session_state.messages = []
                    st.rerun()

            with col_right:
                col_query_editor, col_run_button = st.columns([0.8, 0.2])
                
                with col_query_editor:
                    st.subheader("SPARQL Query Editor")

                # Use the current query in the session state
                if st.session_state.get('update_ace_editor', False):
                    query_to_display = st.session_state["sparql_query"]
                    st.session_state['update_ace_editor'] = False
                    ace_editor_key = str(uuid.uuid4())  # Generate a new unique key
                else:
                    query_to_display = st.session_state.get("ace_editor_content", st.session_state["sparql_query"])
                    ace_editor_key = "ace_editor"

                ace_editor_content = ace.st_ace(
                    value=query_to_display,
                    language="sparql",
                    theme="twilight",       # Choose your preferred theme (twilight, dracula, etc.)
                    show_gutter=True,
                    wrap=True,
                    auto_update=True,
                    min_lines=15,
                    key=ace_editor_key  # Use the unique key
                )

                # Update the session state with the current content of the editor
                st.session_state["ace_editor_content"] = ace_editor_content

                # Add SPARQL endpoint input field below the query editor
                selected_endpoint = st.selectbox("Select SPARQL Endpoint", SPARQL_ENDPOINTS, index=SPARQL_ENDPOINTS.index(st.session_state.get('sparql_endpoint', "https://dbpedia.org/sparql")))

                if selected_endpoint == "Other":
                    sparql_endpoint = st.text_input("Enter SPARQL Endpoint", st.session_state.get('sparql_endpoint', ""))
                else:
                    sparql_endpoint = selected_endpoint

                st.session_state['sparql_endpoint'] = sparql_endpoint

                with col_run_button:
                    if st.button("▶ Run Query", key="run_merged_query", on_click=run_query):
                        st.session_state['query_executed'] = True

                    st.markdown(
                        """
                        <style>
                        .stButton button {
                            background-color: #28a745 !important;
                            color: white !important;
                        }
                        </style>
                        """,
                        unsafe_allow_html=True
                    )

                # Create a placeholder for the success message
                query_placeholder = st.empty()

                # Display the success message in the placeholder
                if 'query_executed' in st.session_state and st.session_state['query_executed']:
                    if 'query_success' in st.session_state and st.session_state['query_success']:
                        context = extract_context(st.session_state["sparql_query"])
                        query_placeholder.success(f"{context}")
                    st.session_state['query_executed'] = False

                # Display the query output below the success message in an expansion section
                
                # Detect columns that contain HTTP URLs and create a LinkColumn for them
                column_config = {}
                for column in st.session_state['df'].columns:
                    # Check if the column contains URLs starting with "http"
                    if st.session_state['df'][column].apply(lambda x: isinstance(x, str) and x.startswith("http")).any():
                        column_config[column] = st.column_config.LinkColumn(
                            column,
                            help=f"More information on {column}"
                        )

                # Use `st.data_editor` to display the DataFrame with LinkColumn
                with st.expander("Query Results"):
                    if not st.session_state['df'].empty:
                        st.data_editor(
                            st.session_state['df'],
                            column_config=column_config,
                            hide_index=True
                        )
                    else:
                        st.write("No data to show yet. Run a SPARQL query first.")

        with tab2:
            st.subheader("Visual Block Builder")
            st.components.v1.iframe("https://leipert.github.io/vsb/dbpedia/#/workspace", height=800, scrolling=True)

def run_query():
    try:
        df = run_sparql_query(
            st.session_state["ace_editor_content"],
            st.session_state['sparql_endpoint']
        )
        st.session_state["df"] = df
        st.session_state["sparql_query"] = st.session_state["ace_editor_content"]
        st.session_state['query_success'] = True
    except Exception as e:
        st.session_state['query_success'] = False
        st.error(f"Error running SPARQL: {e}")

def extract_context(query):
    prompt = f"SPARQL query about <blank> ran successfully! for the following SPARQL query: {query}"
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=100
    )
    return response.choices[0].message["content"].strip()

if __name__ == "__main__":
    main()