# Streamlit SPARQL Query UI
This Streamlit app provides an interactive user interface to filter data, visualize tables or graphs, and execute SPARQL queries. The app is designed with a simple, user-friendly layout to make it easier to interact with and explore data.

## Features
- **Sidebar Filters**: 
  - Quickly filter data using buttons for categories such as Role, Data Type, Layer Depth, Material, and Company.
- **Graph/Table Toggle**:
  - Switch between visual graph representations or tabular data views.
- **SPARQL Query Editor**:
  - View and edit SPARQL queries in a dedicated section.
  - Supports toggling between SPARQL, Visual, and Text views.
  
## Installation
1. Clone this repository
2. Navigate to the project directory:
  ```bash
  cd streamlit-sparql-ui
  ```
3. Install the required dependencies:
  ```bash
  pip install -r requirements.txt
  ```
*(If `requirements.txt` is not available, simply install Streamlit with: `pip install streamlit`.)*

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
└── requirements.txt # Python dependencies (if available)
```

## Customization
Feel free to modify the `app.py` file to:
- Add more filters to the sidebar.
- Integrate graph visualizations using libraries like `plotly` or `matplotlib`.
- Enhance SPARQL query execution with a backend service.

## Requirements
- Python 3.7 or later
- Streamlit

## Future Enhancements
- Dynamic loading of filters from a backend.
- Integration with SPARQL endpoints for real-time query execution.
- Improved graph visualizations and table formatting.
