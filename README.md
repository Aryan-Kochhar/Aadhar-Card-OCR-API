# Aadhaar OCR API

A lightweight Python project that extracts key information from the **front and back images of an Indian Aadhaar card** using **Tesseract OCR** and exposes it through a simple **Flask REST API**.

---

## 🔍 What it does

- Uses image-to-text OCR with `pytesseract`
- Parses:
  - ✅ Name
  - ✅ Date of Birth
  - ✅ Gender
  - ✅ Aadhaar Number
  - ✅ Parent/Guardian Name & Relation
  - ✅ Address
  - ✅ Pincode
- Accepts images through an API or local file path

---

## 📁 Project Structure
├── aadhar_ocr.py # Core OCR logic (modularized functions)
├── app.py # Flask API version using uploaded images
├── test.py # Flask-RESTful variant (same logic, different structure)
├── file1.py # Initial version with local image path + file output
├── extracted_aadhar_data.json # Sample output from file1.py
├── extracted_back_data.json # Sample output from file1.py

---

## 🛠️ Requirements

- Python 3.7+
- Tesseract OCR installed (add to PATH)
- Python libraries:
- bash
- pip install flask flask-restful pytesseract numpy regex

## To Run the files, there's different versions.

Initially, install all the libraries using the requirements.txt file. If you don't know how to, just write this command.

# pip install -r requirements.txt

1. Using **Flask Rest API**
  a. Here, you go to postman or any suitable provider and then give an appropriate **POST REQUEST** for **Front Image** and **Back Image**
     # POST http://localhost:5000/
     # To run the code for this, just type ``` "python test.py" ```
   
  b. Sample response is as: 
  ```
  {
  "Name": "Sid Malhorta",
  "DOB": "28-05-2000",
  "Gender": "Female",
  "Aadhaar": "3425 0653 1151",
  "Parent": "Amit Kumar Tandon",
  "Relation": "S/O",
  "Address": "Merlin Greens, Flat A 1920, Kriparampur, Naskar Para, Chandi, Bishnupur, South 24 Parganas, West Bengal",
  "Pincode": "743503"
  }
```

2. Using **Flask API**
     # Do the above and just type "python app.py"
   
  a. Sample response is as: 
  ```
  {
  "Name": "Sid Malhorta",
  "DOB": "28-05-2000",
  "Gender": "Female",
  "Aadhaar": "3425 0653 1151",
  "Parent": "Amit Kumar Tandon",
  "Relation": "S/O",
  "Address": "Merlin Greens, Flat A 1920, Kriparampur, Naskar Para, Chandi, Bishnupur, South 24 Parganas, West Bengal",
  "Pincode": "743503"
  }
```

3. For running locally,
   a. Go to the file **file1.py**
   b. Give paths for **Front Image** and **Back Image**
    # Now just type "python file1.py"
   c. The extracted data will be stored in the form of JSON files in your system.
     b. Sample response is as:
   
   Front file:
   ```
     {
      "Name": "Sid Malhorta",
      "DOB": "28-05-2000",
      "Gender": "Female",
      "Aadhaar": "3425 0653 1151"
     }
   ```
   Back file:
   ```
     {
    "Parent": "Amit Kumar Tandon",
    "Relation": "S/O",
    "Address": "Merlin Greens, Flat A 1920, Kriparampur, Naskar Para, Chandi, Bishnupur, South 24 Parganas, West Bengal",
    "Pincode": "743503"
    }
   ```
---

# Summary 

| File            | Description                                                             |
| --------------- | ----------------------------------------------------------------------- |
| `file1.py`      | Initial Aadhaar parser using local images and writing JSON output       |
| `aadhar_ocr.py` | Core reusable OCR logic now used by both `app.py` and `test.py`         |
| `app.py`        | Simple Flask API that receives image files via `POST`                   |
| `test.py`       | Enhanced Flask-RESTful version with better structure and error handling |

   
