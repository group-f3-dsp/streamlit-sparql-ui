# Streamlit SPARQL Query UI
This Streamlit app provides an interactive user interface to filter data, visualize tables or graphs, and execute SPARQL queries. The app is designed with a simple, user-friendly layout to make it easier to interact with and explore data.

## Features
- Interactive filters
- SPARQL query execution
- Data visualization

## Installation
1. Clone this repository:
   ```bash
   git clone <repository-url>
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

5. Create a 

.env

 file in the root directory and add your Gemini API key:
   ```plaintext
   GEMINI_API_KEY=your_gemini_api_key_here
   ```

## Acquiring a Gemini API Key
1. Visit the [Gemini API website](https://ai.google.dev/gemini-api/docs).
2. Sign up or log in to your account.
3. Follow the instructions to create a new API key.
4. Copy the API key and add it to your `.env` file as shown above.

## Usage
1. Run the Streamlit app:
   ```bash
   streamlit run app.py
   ```

2. Open your browser and navigate to:
   ```
   http://localhost:8501
   ```

## Project Structure
```plaintext
streamlit-sparql-ui/
│
├── app.py          # Main Streamlit app code
├── README.md       # Documentation for the app
├── requirements.txt # Python dependencies
└── .env            # Environment variables (not tracked by Git)
```

## Requirements
- Python 3.7 or later
- Streamlit

## Running the WebVOWL Server

### Prerequisites
- Node.js

### Steps
1. Download and install Node.js from [Node.js download page](http://nodejs.org/download/).

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

6. Run the WebVOWL server:
   ```bash
   serve deploy/
   ```

7. Access WebVOWL:
   - Open your browser and visit [http://localhost:3000](http://localhost:3000) to use WebVOWL.