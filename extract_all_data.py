import pymupdf
import os
import re
from collections import defaultdict

def extract_student_data_from_pdf(pdf_path):
    """Extrae datos de estudiantes de un informe grupal PDF"""
    students = []
    
    try:
        doc = pymupdf.open(pdf_path)
    except Exception as e:
        print(f"Error abriendo {pdf_path}: {e}")
        return students
    
    # Extraer información de la institución del nombre del archivo
    file_name = os.path.basename(pdf_path)
    institution_match = re.search(r'I\.E\.?\s*([^./]+?)(?:\.pdf|$)', file_name, re.IGNORECASE)
    if institution_match:
        institution = institution_match.group(1).strip()
    else:
        # Intentar otro patrón
        institution_match = re.search(r'I\.E\s+([A-ZÁÉÍÓÚÑ\s]+?)(?:\s*-|\s*\.)', file_name)
        if institution_match:
            institution = institution_match.group(1).strip()
        else:
            institution = "Desconocida"
    
    # Buscar páginas con INFORME DE ASIGNATURAS (GENERAL)
    for page_num in range(len(doc)):
        page = doc[page_num]
        text = page.get_text()
        
        if "INFORME DE ASIGNATURAS (GENERAL)" in text:
            lines = text.split('\n')
            
            # Identificar columnas: MATEMÁTICAS, SOCIALES Y CIUDADANÍA, CIENCIAS NATURALES, INGLES, GRUPO, LECTURA CRÍTICA
            # El orden en el texto es: MATEMÁTICAS, SOCIALES Y CIUDADANÍA, CIENCIAS NATURALES, NOMBRE, INGLES, GRUPO, LECTURA CRÍTICA
            
            i = 0
            while i < len(lines):
                line = lines[i].strip()
                
                # Buscar nombres de estudiantes (líneas que terminan con punto y tienen mayúsculas)
                if re.match(r'^[A-ZÁÉÍÓÚÑ\s]+\.$', line) and len(line) > 10:
                    student_name = line.rstrip(' .').strip()
                    
                    # La siguiente línea debería ser el grupo
                    if i + 1 < len(lines) and re.match(r'^\d+-\d+$', lines[i+1].strip()):
                        group = lines[i+1].strip()
                        
                        # Las siguientes 5 líneas deberían ser las puntuaciones
                        # Orden en el PDF: Matematicas, Sociales, Ciencias, Ingles, Grupo, Lectura Critica
                        # Pero en el texto extraído parece ser diferente
                        
                        # Revisar las líneas después del grupo
                        scores = []
                        j = i + 2
                        while j < len(lines) and len(scores) < 5:
                            try:
                                score = float(lines[j].strip())
                                scores.append(score)
                                j += 1
                            except ValueError:
                                break
                        
                        if len(scores) >= 4:
                            # Asumiendo el orden: Matematicas, Sociales, Ciencias, Naturales, Ingles, Lectura Critica
                            # Basado en lo visto: posiciones 3,4,5,6,7 son las primeras 5 scores antes del nombre
                            # Parece que el orden es: 5 scores antes del nombre, luego nombre, luego grupo, luego 5 scores
                            
                            # Reanalizando: En la página 24 vimos:
                            # Lineas 19-26: 0.0, 0.0, 0.0, 42.0, 58.0, 58.0, 58.0, 80.0 (antes del primer nombre)
                            # Linea 27: BATTA FIGUEROA MAICOL STIVEN .
                            # Linea 28: 11-01
                            # Lineas 29-36: 0.0, 0.0, 0.0, 100.0, 46.0, 54.0, 62.0, 25.0
                            
                            # Parece que hay 8 valores antes de cada nombre
                            # Probablemente: algo, Matematicas, Sociales, Ciencias, algo, Ingles, Lectura, Critica?
                            
                            # Mejor approach: buscar patrones consistentes
                            student_data = {
                                'nombre': student_name,
                                'grupo': group,
                                'institucion': institution,
                                'archivo_origen': os.path.basename(pdf_path),
                                'scores_raw': scores
                            }
                            students.append(student_data)
                        
                        i = j
                    else:
                        i += 1
                else:
                    i += 1
    
    doc.close()
    return students

# Probar con un archivo
test_file = "/workspace/RESULTADOS SIMULACROS I.E-IDEXUD/Resultados I.E LA DESPENSA/1101-InformeGrupo Sim.LosPotros I.E LaDespensa.pdf"
students = extract_student_data_from_pdf(test_file)
print(f"Estudiantes encontrados: {len(students)}")
for s in students[:5]:
    print(s)
