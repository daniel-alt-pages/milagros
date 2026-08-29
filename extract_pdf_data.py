import fitz  # pymupdf
import os

# Probar extracción de un informe grupal para ver la estructura
test_file = "/workspace/RESULTADOS SIMULACROS I.E-IDEXUD/Resultados I.E LA DESPENSA/1101-InformeGrupo Sim.LosPotros I.E LaDespensa.pdf"

doc = fitz.open(test_file)
print(f"Total páginas: {len(doc)}")

# Extraer texto de las primeras 30 páginas para encontrar la página 23
for page_num in range(min(30, len(doc))):
    page = doc[page_num]
    text = page.get_text()
    if "INFORME DE ASIGNATURAS" in text or "ASIGNATURAS" in text:
        print(f"\n=== PÁGINA {page_num + 1} ===")
        lines = text.split('\n')
        for i, line in enumerate(lines[:60]):
            print(f"{i}: {repr(line)}")
        
doc.close()
