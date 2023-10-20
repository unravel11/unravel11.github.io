import os
import json

def generate_pdf_list(directory="pdf"):
    pdf_list = []
    for subdir, _, files in os.walk(directory):
        category = os.path.basename(subdir)
        for file in files:
            if file.endswith('.pdf'):
                pdf_list.append({"category": category, "name": file})

    with open('pdfList.json', 'w') as f:
        json.dump(pdf_list, f, indent=4)

if __name__ == "__main__":
    generate_pdf_list()
