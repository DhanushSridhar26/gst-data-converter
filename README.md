# GST Data Converter

## Overview

GST Data Converter is a Streamlit app that processes ZIP files containing GSTR-2B JSON files, extracts invoice data by month and category, and generates an Excel report with multiple sheets for easy analysis.

## Features

- Upload a ZIP file containing multiple GSTR-2B JSON files.
- Automatically detect months from filenames.
- Select specific month(s) to filter data.
- Export filtered data into an Excel file with separate sheets per category.
- Download the Excel report directly from the app.

## Installation

Make sure you have Python 3.7 or higher installed.  
Install required packages with:

```bash
pip install streamlit pandas openpyxl
