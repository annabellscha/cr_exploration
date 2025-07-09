# Commercial Register Data Extraction & Analysis Platform

A comprehensive platform for extracting, processing, and analyzing German commercial register data with focus on angel investor networks and startup ecosystems.

## 🚀 Overview

This platform consists of multiple microservices that work together to:
- Extract company data from German commercial registers
- Process and standardize extracted information using LLMs
- Analyze angel investor networks and startup ecosystems
- Generate insights through data visualization and network analysis

## 📁 Project Structure

```
cr_exploration/
├── cr_extraction/           # Commercial register data extraction service
├── llm_data_standardization/ # LLM-powered data standardization
├── structured_info/         # Structured information extraction
├── structured_info_for_shareholders/ # Shareholder-specific data processing
├── table_extraction/        # PDF table extraction service
├── notebooks/              # Jupyter notebooks for data analysis
├── tests/                  # Test suite
└── template.env            # Environment variables template
```

## 🔧 Services

### 1. Commercial Register Extraction (`cr_extraction/`)
**Purpose**: Extract company and shareholder data from German commercial registers

**Key Functions**:
- `search_companies()`: Search companies by name
- `search_companies_by_id()`: Search companies by ID
- `download_files()`: Download commercial register documents
- `get_shareholder_structured_info()`: Extract structured shareholder information

**Dependencies**: Flask, Google Cloud Storage, MechanicalSoup, BeautifulSoup

### 2. LLM Data Standardization (`llm_data_standardization/`)
**Purpose**: Standardize extracted data using OpenAI's language models

**Key Functions**:
- `standardize_data()`: Process and standardize company data

**Dependencies**: OpenAI, Pandas, Flask

### 3. Structured Information Extraction (`structured_info/`)
**Purpose**: Extract structured information from commercial register documents

**Key Functions**:
- `get_structured_content()`: Extract structured content from documents

**Dependencies**: OpenAI, Pandas, Flask

### 4. Table Extraction (`table_extraction/`)
**Purpose**: Extract tabular data from PDF documents

**Key Functions**:
- `extract_table()`: Extract tables from PDF files

**Dependencies**: OpenAI, Pandas, Flask

## 📊 Data Analysis

The `notebooks/` directory contains comprehensive analysis of angel investor networks:

- **Network Analysis**: Angel investor co-investment networks
- **Descriptive Statistics**: Analysis of angels, startups, and network characteristics
- **Community Detection**: Identification of investor communities
- **Geographic Analysis**: Regional investment patterns
- **Industry Analysis**: Investment patterns across sectors

### Key Datasets
- `angels.csv`: Angel investor profiles and characteristics
- `startups.csv`: Startup company information
- `shareholder_relations_angel.csv`: Angel-startup investment relationships

## 🛠️ Setup & Installation

### Prerequisites
- Python 3.8+
- Google Cloud Platform account
- OpenAI API key

### Environment Setup
1. Copy `template.env` to `.env`
2. Configure your environment variables:
```bash
GOOGLE_APPLICATION_CREDENTIALS=Path/To/Google/Key.json
OPENAI_API_KEY=your-openai-api-key
ENV=prod
FORM_RECOGNIZER_ENDPOINT=your-form-recognizer-endpoint
FORM_RECOGNIZER_KEY=your-form-recognizer-key
```

### Installation
```bash
# Install dependencies for each service
cd cr_extraction && pip install -r requirements.txt
cd ../llm_data_standardization && pip install -r requirements.txt
cd ../structured_info && pip install -r requirements.txt
cd ../table_extraction && pip install -r requirements.txt
```

## 🚀 Deployment

### Google Cloud Functions
Each service is designed to deploy as a Google Cloud Function:

```bash
# Deploy commercial register extraction
gcloud functions deploy search_companies \
  --runtime python39 \
  --trigger-http \
  --source cr_extraction/

# Deploy data standardization
gcloud functions deploy standardize_data \
  --runtime python39 \
  --trigger-http \
  --source llm_data_standardization/
```

### Local Development
```bash
# Run services locally using Functions Framework
cd cr_extraction && functions-framework --target search_companies --debug
cd ../llm_data_standardization && functions-framework --target standardize_data --debug
```

## 📈 Usage Examples

### Search Companies
```python
import requests

# Search for a company
response = requests.post('your-function-url/search_companies', 
                       json={'name': 'Company Name'})
companies = response.json()
```

### Download Documents
```python
# Download commercial register documents
response = requests.post('your-function-url/download_files',
                       json={
                           'company_id': 'company_id',
                           'documents': ['extract', 'shareholder_list']
                       })
```

### Standardize Data
```python
# Standardize extracted data
response = requests.post('your-function-url/standardize_data',
                       json={'company_id': 'company_id'})
standardized_data = response.json()
```

## 🧪 Testing

Run the test suite:
```bash
python -m pytest tests/
```

## 📊 Data Analysis Workflow

1. **Data Extraction**: Use `cr_extraction` to gather company data
2. **Data Processing**: Use `llm_data_standardization` to clean and standardize data
3. **Information Extraction**: Use `structured_info` and `table_extraction` for detailed analysis
4. **Network Analysis**: Use notebooks for angel investor network analysis

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📄 License

This project is proprietary and confidential.

## 🔗 Dependencies

- **Web Scraping**: MechanicalSoup, BeautifulSoup
- **Cloud Services**: Google Cloud Storage, Google Cloud Functions
- **AI/ML**: OpenAI API
- **Data Processing**: Pandas, NumPy
- **Network Analysis**: NetworkX
- **Visualization**: Matplotlib, Plotly

---

**Note**: This platform is designed for research and analysis of German commercial register data. Ensure compliance with data protection regulations when using this tool. 