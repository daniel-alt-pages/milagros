import pymupdf

# Inspect one PDF to understand its structure
pdf_path = "/workspace/RESULTADOS SIMULACROS I.E-IDEXUD/Resul.Sim I.E CIUDADELA SUCRE/1101 Resul.Individu SimLosPotros I.E C.Sucre.pdf"

doc = pymupdf.open(pdf_path)
print(f"Number of pages: {len(doc)}")

for page_num, page in enumerate(doc):
    print(f"\n=== PAGE {page_num + 1} ===")
    text = page.get_text()
    print(text[:3000])  # First 3000 chars
    if len(text) > 3000:
        print("... [truncated]")
    break  # Just first page for now

doc.close()
