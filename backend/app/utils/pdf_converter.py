import os
from PyPDF2 import PdfReader

def convert_pdfs_to_txt(source_folder, output_folder):
    os.makedirs(output_folder, exist_ok=True)

    for file in os.listdir(source_folder):
        if file.endswith(".pdf"):
            pdf_path = os.path.join(source_folder, file)
            reader = PdfReader(pdf_path)
            text = "\n".join([page.extract_text() or "" for page in reader.pages])

            txt_filename = file.replace(".pdf", ".txt")
            txt_path = os.path.join(output_folder, txt_filename)

            with open(txt_path, "w", encoding="utf-8") as f:
                f.write(text)
            print(f"✅ {file} converti en {txt_filename}")
