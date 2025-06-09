from PIL import Image
import pytesseract
import numpy as np
import regex as re
from datetime import datetime
#This is the tesseract path on my system
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

result = {
    "Name": None,
    "DOB": None,
    "Gender": None,
    "Aadhaar": None
}

information = {
    "Parent": None,
    "Relation": None,
    "Address": None,
    "Pincode": None
}

def get_address(text):
    global information
    lines = [line.strip() for line in text.split('\n') if line.strip()]
    address_lines = []
    relation_keywords = ['D/O', 'S/O', 'W/O']
    parent_flag = False
    aadhaar_pattern = re.compile(r'\b\d{4}\s?\d{4}\s?\d{4}\b')

    for i, line in enumerate(lines):
        #check parent/relation
        for keyword in relation_keywords:
            if keyword in line:
                information["Relation"] = keyword
                # Clean and extract parent name before address
                name_part = line.split(keyword)[-1].strip()
                name_match = re.search(r'([A-Z][a-zA-Z.]+\s?){1,4}', name_part)
                if name_match:
                    name_cleaned = re.split(r'\b(H\.?|Flat|No|House|Street|Road|\d{1,4})', name_part)[0].strip()
                    information["Parent"] = name_cleaned
        
        #check address
        if 'Address:' in line:
            for j in range(i, min(i + 6, len(lines))):
                # Skip lines with Aadhaar, mobile, UIDAI, or garbage
                if aadhaar_pattern.search(lines[j]) or re.search(r'(uidai|mobile|gov\.in|1947|fe\b)', lines[j], re.IGNORECASE):
                    break
                cleaned_line = re.sub(r'[^A-Za-z0-9\s,]', '', lines[j])
                if len(cleaned_line) < 4 or re.match(r'^[^\w]*$', cleaned_line):
                    continue

                
                # remove "Address" prefix if present
                if j == i:
                    cleaned_line = re.sub(r'Address[:\s]*', '', cleaned_line, flags=re.IGNORECASE)

                if cleaned_line:
                    address_lines.append(cleaned_line.title())


    #if no "address" found, we take line after relation
    if not address_lines and information["Relation"]:
        for i, line in enumerate(lines):
            if information["Relation"] in line:
                for j in range(i + 1, min(i + 7, len(lines))):
                    # Stop if line has pincode or Aadhaar
                    if aadhaar_pattern.search(lines[j]) or re.search(r'\b\d{6}\b', lines[j]):
                        break
                    cleaned_line = re.sub(r'[^A-Za-z0-9\s,]', '', lines[j])
                    if cleaned_line:
                        address_lines.append(cleaned_line.title())
                break

    if address_lines:
        full_addr = ', '.join(address_lines)
        full_addr = re.sub(r'\s+,', ',', full_addr)  # fix space before comma
        full_addr = re.sub(r',\s*,', ',', full_addr)  # fix double commas
        information["Address"] = full_addr.strip()

        #getting pincode
        pincode_pattern = re.search(r'\b\d{6}\b', full_addr)
        if pincode_pattern:
            information["Pincode"] = pincode_pattern.group(0)
            
#cleaning the data 
def clean_name(name):
    name = name.replace('[', '').replace(']', '')
    return re.sub(r'[^A-Za-z\s.]', '', name).strip()

#Getting the Aadhar Number
def aadhaar_number(text):
    global result
    text=text.replace('O','0').replace('B','8').replace('I','1')
    # 4 digit, space, repeat
    number_pattern = r'\b\d{4}\s?\d{4}\s?\d{4}\b'
    aadhaar_match= re.search(number_pattern,text)

    if aadhaar_match:
        #remove the space
        aadhaar_no=aadhaar_match.group().replace(" ","")
        extracted_no= (f"{aadhaar_no[0:4]} {aadhaar_no[4:8]} {aadhaar_no[8:12]}")
        result['Aadhaar']=extracted_no
    else:
        print("Aadhaar number not found")

#Getting the Name 
def get_name(text):
    global result
    lines = [line.strip() for line in text.split('\n') if line.strip()]

    for i, line in enumerate(lines):
        if "Name:" in line or "नाम/Name:" in line:
            name_part = line.split("Name:")[-1].strip()
            name_part = name_part.replace('[', '').replace(']', '')
            if name_part:
                result["Name"] = clean_name(name_part)
                return
            elif i + 1 < len(lines):
                next_line = lines[i + 1].replace('[', '').replace(']', '')
                result["Name"] = clean_name(next_line)
                return

    # getting line above dob 
    dob_keywords = ['DOB', 'Date of Birth', 'जन्म तिथि', 'Birth', 'irtyD08']  # <- added OCR variant
    dob_index = -1

    for i, line in enumerate(lines):
        if any(keyword in line for keyword in dob_keywords):
            dob_index = i
            break

    if dob_index > 0:
        raw_line = lines[dob_index - 1].replace('[', '').replace(']', '')
        if not any(char.isdigit() for char in raw_line):
            cleaned_name = clean_name(raw_line)
            result["Name"] = cleaned_name
            return

    print("Name not found")



def get_dob(text):
    global result
    dob_patterns = [
        r'(?:DOB|Date of Birth|जन्म तिथि)[:/]?\s*(\d{2}[/-]\d{2}[/-]\d{4})',
        r'(?:DOB|Date of Birth|जन्म तिथि)[:/]?\s*(\d{4}[/-]\d{2}[/-]\d{2})',
        r'\b(\d{2}[/-]\d{2}[/-]\d{4})\b',
        r'\b(\d{4}[/-]\d{2}[/-]\d{2})\b'
    ]
    
    for pattern in dob_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            dob_str = match.group(1)
            try:
                # Try to parse the date in different formats
                for fmt in ('%d/%m/%Y', '%d-%m-%Y', '%Y/%m/%d', '%Y-%m-%d'):
                    try:
                        dob = datetime.strptime(dob_str, fmt).date()
                        result["DOB"] = dob.strftime('%d-%m-%Y')
                        return dob
                    except ValueError:
                        continue
            except Exception as e:
                print(f"Error parsing date: {e}")
                continue
    
    print("Date of Birth not found")
    return None

def get_gender(text):
    global result
    """Extract Gender from text"""
    gender_patterns = [
        r'(?:Gender|Sex|लिंग)[:/]?\s*(Male|Female|Transgender|M|F|T|महिला|पुरुष)',
        r'\b(Male|Female|Transgender|M|F|T)\b'
    ]
    
    gender_mapping = {
        'M': 'Male',
        'F': 'Female',
        'T': 'Transgender',
        'Male': 'Male',
        'Female': 'Female',
        'Transgender': 'Transgender',
        'पुरुष': 'Male',
        'महिला': 'Female'
    }
    
    for pattern in gender_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            gender = match.group(1).capitalize()
            gender = gender_mapping.get(gender, gender)
            result["Gender"] = gender
            return gender
    print("Gender not found")
    return None

#_main_

#Loading the image 
front = r'C:\Programming\Coding\.aadhar\Aadhar Front\img2.jpg'
image_front = np.array(Image.open(front))
text_front = pytesseract.image_to_string(image_front, lang = 'eng')
print("Raw OCR Text:\n",text_front,"\n"+"-"*50)
get_name(text_front)
aadhaar_number(text_front)
get_dob(text_front)
get_gender(text_front)

back = r'C:\Programming\Coding\.aadhar\Aadhar Back\img6.png'
image_back = np.array(Image.open(back))
text_back = pytesseract.image_to_string(image_back, lang = 'eng')
get_address(text_back)

#saving front info in file

import json
output_path = "extracted_aadhar_data.json"

with open(output_path, "w") as f:
    json.dump(result, f, indent=4)

print(f"\n Saved data in {output_path}")

output_path_back = "extracted_back_data.json"
with open (output_path_back,"w") as f:
    json.dump(information,f,indent=4)
    
print(f"\n Saved data in {output_path_back}")
