import os
import json

def generate_pdf_list(directory="pdf"):
    pdf_list = []
    for subdir, _, files in os.walk(directory):
        category = os.path.basename(subdir)
        for file in files:
            if file.endswith('.pdf'):
                pdf_list.append({"category": category, "name": file})
    ##根据pdf文件名排序，文件名为XX_数字_中文名.pdf,根据数字大小排序
    pdf_list = sorted(pdf_list, key=lambda x: int(x['name'].split('_')[1]))

    with open('pdfList.json', 'w') as f:
        json.dump(pdf_list, f, indent=4)

if __name__ == "__main__":
    generate_pdf_list()
