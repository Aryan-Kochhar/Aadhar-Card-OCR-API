# aadhar_ocr.py
from PIL import Image
import pytesseract
import numpy as np 
import regex as re
from datetime import datetime

pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

def clean_ocr_text(text):
    return text.replace('O', '0').replace('I', '1').replace('B', '8')

def clean_name(name):
    name = name.replace('[', '').replace(']', '')
    return re.sub(r'[^A-Za-z\s.]', '', name).strip()

def extract_front_data(text):
    result = {
        "Name": None,
        "DOB": None,
        "Gender": None,
        "Aadhaar": None
    }

    lines = [line.strip() for line in text.split('\n') if line.strip()]

    # Name
    for i, line in enumerate(lines):
        if "Name:" in line or "नाम/Name:" in line:
            name_part = line.split("Name:")[-1].strip()
            if name_part:
                result["Name"] = clean_name(name_part)
                break
            elif i + 1 < len(lines):
                result["Name"] = clean_name(lines[i + 1])
                break

    # getting line above dob
    dob_keywords = ['DOB', 'Date of Birth', 'जन्म तिथि', 'Birth']
    for i, line in enumerate(lines):
        if any(k in line for k in dob_keywords) and i > 0:
            prev_line = lines[i - 1]
            if not any(char.isdigit() for char in prev_line):
                result["Name"] = clean_name(prev_line)
                break

    # DOB
    dob_patterns = [
        r'(?:DOB|Date of Birth|जन्म तिथि)[:/]?\s*(\d{2}[/-]\d{2}[/-]\d{4})',
        r'(?:DOB|Date of Birth|जन्म तिथि)[:/]?\s*(\d{4}[/-]\d{2}[/-]\d{2})',
        r'\b(\d{2}[/-]\d{2}[/-]\d{4})\b',
        r'\b(\d{4}[/-]\d{2}[/-]\d{2})\b'
    ]
    for pattern in dob_patterns:
        match = re.search(pattern, text)
        if match:
            dob_str = match.group(1)
            for fmt in ('%d/%m/%Y', '%d-%m-%Y', '%Y/%m/%d', '%Y-%m-%d'):
                try:
                    dob = datetime.strptime(dob_str, fmt).date()
                    result["DOB"] = dob.strftime('%d-%m-%Y')
                    break
                except:
                    continue

    # getting gender
    gender_patterns = [
        r'(?:Gender|Sex|लिंग)[:/]?\s*(Male|Female|Transgender|M|F|T)',
        r'\b(Male|Female|Transgender|M|F|T)\b'
    ]
    gender_mapping = {
        'M': 'Male', 'F': 'Female', 'T': 'Transgender',
        'Male': 'Male', 'Female': 'Female', 'Transgender': 'Transgender'
    }
    for pattern in gender_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            gender = match.group(1).capitalize()
            result["Gender"] = gender_mapping.get(gender, gender)
            break

    # Aadhaar
    number_pattern = r'\b\d{4}\s?\d{4}\s?\d{4}\b'
    aadhaar_match = re.search(number_pattern, clean_ocr_text(text))
    if aadhaar_match:
        num = aadhaar_match.group().replace(" ", "")
        result["Aadhaar"] = f"{num[:4]} {num[4:8]} {num[8:]}"

    return result

def extract_back_data(text):
    info = {
        "Parent": None,
        "Relation": None,
        "Address": None,
        "Pincode": None
    }

    lines = [line.strip() for line in text.split('\n') if line.strip()]
    address_lines = []
    relation_keywords = ['D/O', 'S/O', 'W/O']
    aadhaar_pattern = re.compile(r'\b\d{4}\s?\d{4}\s?\d{4}\b')

    for i, line in enumerate(lines):
        #check parent/relation
        for keyword in relation_keywords:
            if keyword in line:
                info["Relation"] = keyword
                #clean and extract parent name before address
                name_part = line.split(keyword)[-1].strip()
                name_cleaned = re.split(r'\b(H\.?|Flat|No|House|Street|Road|\d{1,4})', name_part)[0].strip()
                info["Parent"] = name_cleaned

        #check address
        if 'Address:' in line:
            for j in range(i, min(i + 6, len(lines))):

                #skip lines having aadhaar,mobile, uidai or garbage
                if aadhaar_pattern.search(lines[j]) or re.search(r'(uidai|mobile|gov\.in|1947)', lines[j], re.IGNORECASE):
                    break
                cleaned = re.sub(r'[^A-Za-z0-9\s,]', '', lines[j])

                #remove "address" prefix if present
                if j == i:
                    cleaned = re.sub(r'Address[:\s]*', '', cleaned, flags=re.IGNORECASE)
                if cleaned:
                    address_lines.append(cleaned.title())

    #if no "address" found, we take line after relation
    if not address_lines and info["Relation"]:
        for i, line in enumerate(lines):
            if info["Relation"] in line:
                for j in range(i + 1, min(i + 7, len(lines))):
                    if aadhaar_pattern.search(lines[j]) or re.search(r'\b\d{6}\b', lines[j]):
                        break
                    cleaned = re.sub(r'[^A-Za-z0-9\s,]', '', lines[j])
                    if cleaned:
                        address_lines.append(cleaned.title())
                break

    if address_lines:
        addr = ', '.join(address_lines)
        addr = re.sub(r'\s+,', ',', addr)
        addr = re.sub(r',\s*,', ',', addr)
        info["Address"] = addr.strip()
        pincode_match = re.search(r'\b\d{6}\b', addr)
        if pincode_match:
            info["Pincode"] = pincode_match.group(0)

    return info

#__main__ 

def process_aadhar(front_path, back_path):
    try:
        image_front = np.array(Image.open(front_path))
        text_front = pytesseract.image_to_string(image_front, lang='eng')
        front_data = extract_front_data(text_front)

        image_back = np.array(Image.open(back_path))
        text_back = pytesseract.image_to_string(image_back, lang='eng')
        back_data = extract_back_data(text_back)

        return {**front_data, **back_data}
    except Exception as e:
        return {"error": str(e)}

