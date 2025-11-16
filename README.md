# Thinking Machine - CSV Processing Pipeline

**A serverless Azure Functions application that processes CSV files containing text with coordinates, grouping them horizontally and vertically.**

---

## Architecture

HTTP Request → Upload CSV → Queue Message → Queue Trigger → Process CSV → Output JSON

- **HTTP Trigger**: Accepts CSV uploads, stores in blob storage, queues for processing
- **Queue Trigger**: Processes CSV files, groups text by coordinates, outputs JSON results
- **Blob Storage**: Stores uploaded CSV files
- **Queue**: Coordinates async processing

---

## Features

- **Upload CSV files** via HTTP endpoint
- **Async processing** via queue triggers
- **Horizontal grouping** by Y coordinate
- **Vertical grouping** by X coordinate
- **JSON output** with grouped results
- **Local development** with Azurite (Azure Storage emulator)

---

## Project Structure

thinking-machine-api/\
├── function_app.py # Azure Functions (HTTP & Queue triggers)\
├── processing_utils.py # CSV processing and grouping logic\
├── storage_utils.py # Blob storage and queue operations\
├── test_processing.py # Unit tests for processing logic\
├── clear_poison.py # Utility to clear poison queues\
├── host.json # Functions runtime configuration\
├── local.settings.json # Local environment variables\
├── requirements.txt # Python dependencies\
└── README.md # This file

---

## Prerequisites

**Before you begin, ensure you have the following installed:**

- **Python 3.11**
- **Azure Functions Core Tools**
- **Docker** (for Azurite storage emulator)

---

## Local Development Setup

### 1. Install Dependencies

```bash
# Create virtual environment
python -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Install Azure Functions Core Tools
npm install -g azure-functions-core-tools@4 --unsafe-perm true
```

---

### 2. Start Azurite (Storage Emulator)

```bash
# Run Azurite in Docker (in a separate terminal)
docker run -p 10000:10000 -p 10001:10001 -p 10002:10002 mcr.microsoft.com/azure-storage/azurite
```

Note: Keep this terminal running - Azurite provides local Azure Storage emulation for blobs, queues, and tables.

---

### 3. Run the Application

```bash
# Start Azure Functions (in your project terminal)
func start
```

# The HTTP endpoint will be available at:

# http://localhost:7071/api/UploadCsv

Tip: You should see your functions loading and the local development server starting up.

---

## API Usage

### Upload CSV for Processing

```bash
curl -X POST http://localhost:7071/api/UploadCsv \
  -H "Content-Type: text/csv" \
  -d "text,x,y
Hello,10,10
World,12,10
This,50,20
Is,52,20
Test,55,20
Example,100,50
Data,105,50
Row,50,10"
```

---

### Processing Results

The queue trigger processes the CSV and outputs JSON grouping results in **two ways**:

1. **Writes to local JSON file** in the project root:
   results_upload-20251116T140459562055.json

2. **Logs to console** for immediate visibility

**Example output file:**

```json
{
  "horizontal_groups": [
    { "y": 10, "texts": ["Hello", "World"] },
    { "y": 20, "texts": ["This", "Is", "Test"] },
    { "y": 50, "texts": ["Example", "Data"] }
  ],
  "vertical_groups": [
    { "x": 10, "texts": ["Hello"] },
    { "x": 12, "texts": ["World"] },
    { "x": 50, "texts": ["This"] },
    { "x": 52, "texts": ["Is"] },
    { "x": 55, "texts": ["Test"] },
    { "x": 100, "texts": ["Example"] },
    { "x": 105, "texts": ["Data"] }
  ]
}
```

Note: Each CSV upload creates a separate results file with timestamp, providing a persistent audit trail.

---

## CSV Format

**The CSV must have the following columns:**

- `text`: The text content (string)
- `x`: X coordinate (numeric)
- `y`: Y coordinate (numeric)

**Example CSV:**

```csv
text,x,y
Hello,10,10
World,12,10
This,50,20
Is,52,20
Test,55,20
Example,100,50
Data,105,50
```

---

## Grouping Algorithm

### Horizontal Groups

- Groups text entries with the same Y coordinate
- Entries are considered on the same horizontal line if they share the same Y value

### Vertical Groups

- Groups text entries with the same X coordinate
- Entries are considered in the same vertical column if they share the same X value

---

## Running Tests

```bash
# Run all unit tests
python -m pytest tests/test_processing.py -v
```

---

## Utility Scripts

### Clear Poison Queue

If messages fail processing multiple times, they go to a poison queue. Clear it with:

```bash
python clear_poison.py
```

When to use: If you see "Message has reached MaxDequeueCount of 5" errors in your logs.

---

## Configuration Files

### host.json

Configures Azure Functions runtime settings, logging levels, and queue polling intervals.

### local.settings.json

Contains connection strings and environment variables for local development.

---

## Troubleshooting

### Common Issues

1. **Queue messages going to poison queue**

   - Check function logs for processing errors
   - Use `clear_poison.py` to reset the queue

2. **Storage connection issues**
   - Ensure Azurite is running in Docker
   - Verify connection strings in `local.settings.json`

---

## Development Notes

- The system uses **Azure Storage Queues** for reliable async processing
- **Blob storage** provides durable file storage for uploaded CSVs
- All coordinates are **rounded down to whole numbers** for grouping consistency
- The solution is designed for **high throughput** scenarios
- **Comprehensive unit tests** ensure processing logic reliability

---

** Thinking Machine's serverless CSV processing pipeline is ready to use!**
