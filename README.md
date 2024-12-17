# Hygwell Internship Assignment

This repository contains the code and analysis for two assignments from the Hygwell internship:

## Overview
1. **FastAPI Backend** - A service that processes web URLs and PDFs, allowing queries via a chat API.
2. **Web Traffic Analysis** - Insights derived from `traffic.csv` using Python, Pandas, and SciPy.

---

## Assignment 1: FastAPI Backend Service

### APIs
1. **Process URL** (`POST /process_url`)
   - Input: `{ "url": "https://example.com" }`
   - Scrapes, cleans, and stores content.
   - Response: `chat_id` and success message.

2. **Process PDF** (`POST /process_pdf`)
   - Input: PDF file (multipart/form-data).
   - Extracts, cleans, and stores text.
   - Response: `chat_id` and success message.

3. **Chat API** (`POST /chat`)
   - Input: `chat_id` and query.
   - Uses embeddings to find relevant responses.
   - Response: Most relevant text.

### Deployment
- Use Docker to containerize and deploy the application.

---

## Assignment 2: Web Traffic Analysis (TODO)

### Tasks Addressed
1. **Pageview Analysis**
   - Total pageviews and daily average.
2. **Event Distribution**
   - Count and distribution of recorded events.
3. **Geographical Insights**
   - Identify contributing countries.
4. **Click-Through Rate (CTR)**
   - Overall CTR and variation across links.
5. **Correlation Analysis**
   - Check for relationships between `clicks` and `pageviews`.

---

## Technologies Used
- **FastAPI**, **Python**, **Pandas**, **SciPy**, **Docker**, **BeautifulSoup**.

---


