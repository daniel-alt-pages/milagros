import pymupdf

# Analizar la estructura completa de una página
test_file = "/workspace/RESULTADOS SIMULACROS I.E-IDEXUD/Resultados I.E LA DESPENSA/1101-InformeGrupo Sim.LosPotros I.E LaDespensa.pdf"

doc = pymupdf.open(test_file)

# Página 24 tiene INFORME DE ASIGNATURAS (GENERAL)
page = doc[23]  # página 24 (index 23)
text = page.get_text()
lines = text.split('\n')

print("=== ESTRUCTURA COMPLETA DE LA PÁGINA 24 ===")
for i, line in enumerate(lines):
    print(f"{i:3d}: {repr(line)}")

doc.close()
