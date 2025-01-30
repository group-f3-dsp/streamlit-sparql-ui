# Streamlit SPARQL Query UI
This Streamlit app provides an interactive user interface to visualize tables or graphs, and execute SPARQL queries. The app is designed with a simple, user-friendly layout to make it easier to interact with and explore data.

## Index
1. [Features](#features)  
2. [Installation](#installation)  
3. [Usage](#usage)  
4. [Project Structure](#project-structure)  
5. [Requirements](#requirements)  
6. [Running the WebVOWL Server](#running-the-webvowl-server)  
7. [Using OWL2VOWL](#using-owl2vowl)  
8. [Contributing](#contributing)  
9. [License](#license)  
10. [Technologies Used](#technologies-used)

## Features
- Data visualization
- SPARQL query execution
- Chat interface aware of the current SPARQL query
- Integration with WebVOWL for visualizing ontologies

## Installation
1. Clone this repository:
   ```bash
   git clone https://github.com/group-f3-dsp/streamlit-sparql-ui.git
   cd streamlit-sparql-ui
   ```

2. Set up the virtual environment:
   ```bash
   python -m venv .venv
   ```

3. Activate the virtual environment:
   - On Windows:
     ```bash
     .venv\Scripts\activate
     ```
   - On macOS/Linux:
     ```bash
     source .venv/bin/activate
     ```

4. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

5. Set up your OpenAI API key and Gemini API key in the Streamlit secrets:
   ```sh
   echo "[secrets]" > .streamlit/secrets.toml
   echo "OPENAI_API_KEY = 'your-openai-api-key'" >> .streamlit/secrets.toml
   echo "GEMINI_API_KEY = 'your-gemini-api-key'" >> .streamlit/secrets.toml
   ```

## Usage
1. Run the Streamlit app:
   ```bash
   streamlit run main.py
   ```

2. Open your browser and navigate to:
   ```
   http://localhost:8501
   ```

## Project Structure
```plaintext
streamlit-sparql-ui/
│
├── .streamlit/       # Streamlit configuration and secrets
   ├── secrets.toml
├── archive/          # Directory containing archive code
├── data/             # Directory containing ontology and example files
│   ├── example.owl
│   ├── example.json
│   ├── dbpedia_ontology.owl
│   ├── dbpedia_ontology.json
│   └── smallTest.md
├── main.py           # Main Streamlit app code
├── README.md         # Documentation for the app
├── requirements.txt  # Python dependencies
└── sparql_utils.py   # Utility functions for running SPARQL queries
└── chat_utils.py     # Utility functions for the Gemini chat
└── config.py         # Configuration file
```

## Requirements
- [Python](https://python.org/downloads) 3.13.0 or later
- [Streamlit](https://docs.streamlit.io/get-started/installation) 1.41.1 or later
- [pip](https://pypi.org/project/pip/) version 24.2 or later

## Running the WebVOWL Server

### Prerequisites
- Node.js

### Steps
1. Download and install Node.js from [Node.js download page](https://nodejs.org/en/download))

2. Clone the WebVOWL repository:
   ```bash
   git clone https://github.com/VisualDataWeb/WebVOWL.git
   cd WebVOWL
   ```

3. Install dependencies and build the project:
   ```bash
   npm install
   ```

4. Build the project:
   ```bash
   npm run-script release
   ```

5. Install `serve` globally:
   ```bash
   npm install serve -g
   ```

6. Run the WebVOWL server locally:
   ```bash
   serve deploy/
   ```

7. Access WebVOWL:
   - Open your browser and visit [http://localhost:3000](http://localhost:3000) to use WebVOWL

## Using OWL2VOWL

With OWL2VOWL, you can convert an OWL file to JSON. Follow these steps to set up and use OWL2VOWL:

1. **Build the Docker image**:
    ```sh
    docker build -t owl2vowl/owl2vowl .
    ```

2. **Run the Docker container**:
    ```sh
    docker run --rm -d -p 8080:8080 owl2vowl/owl2vowl
    ```

3. **Convert an OWL file to JSON**:
    - First, get the timestamp:
        ```sh
        curl -X GET http://localhost:8080/timestamp
        ```

    - Then, supply the OWL file and get the JSON back:
        ```sh
        curl -X POST -F "file=@path/to/your/file.owl" http://localhost:8080/convert
        ```

    Replace `path/to/your/file.owl` with the actual path to your OWL file.

## Contributing

Feel free to open issues or submit pull requests if you have any improvements or bug fixes.

## License

This project is licensed under the GPL-3.0 license.

## Technologies Used

![Python](https://skillicons.dev/icons?i=python)
![Docker](https://skillicons.dev/icons?i=docker)
![Node.js](https://skillicons.dev/icons?i=nodejs)
