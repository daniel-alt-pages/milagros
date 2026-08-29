import pymupdf
import os
import re
import pandas as pd
from pathlib import Path

def extract_institution_name(filepath):
    """Extrae el nombre de la institución desde la ruta del archivo"""
    # Obtener solo el nombre del directorio que contiene la información de la I.E.
    dir_name = os.path.basename(os.path.dirname(filepath))
    
    # Patrones comunes en los nombres de directorios
    patterns = [
        r'I\.E\.?\s*([A-ZÁÉÍÓÚÑ\s]+?)(?:\s*$)',  # I.E. NOMBRE
        r'I\.E\s+([A-ZÁÉÍÓÚÑ\s]+)',  # I.E NOMBRE
        r'Resul\.?Simu?\s*I\.E\s+([A-ZÁÉÍÓÚÑ\s]+)',  # Resul.Simu I.E NOMBRE
    ]
    
    for pattern in patterns:
        match = re.search(pattern, dir_name, re.IGNORECASE)
        if match:
            return match.group(1).strip()
    
    # Si no se encuentra, usar el nombre del directorio completo
    return dir_name

def extract_student_data_from_pdf(pdf_path):
    """Extrae datos de estudiantes de un informe grupal PDF"""
    students = []
    
    try:
        doc = pymupdf.open(pdf_path)
    except Exception as e:
        print(f"Error abriendo {pdf_path}: {e}")
        return students
    
    institution = extract_institution_name(pdf_path)
    
    for page_num in range(len(doc)):
        page = doc[page_num]
        text = page.get_text()
        
        if "INFORME DE ASIGNATURAS (GENERAL)" in text:
            lines = text.split('\n')
            
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
                        scores = []
                        j = i + 2
                        while j < len(lines) and len(scores) < 5:
                            try:
                                score = float(lines[j].strip())
                                scores.append(score)
                                j += 1
                            except ValueError:
                                break
                        
                        if len(scores) == 5:
                            # Orden de columnas según encabezados:
                            # MATEMÁTICAS, SOCIALES Y CIUDADANÍA, CIENCIAS NATURALES, INGLÉS, LECTURA CRÍTICA
                            student_data = {
                                'institucion': institution,
                                'nombre': student_name,
                                'grupo': group,
                                'matematicas': scores[0],
                                'sociales_ciudadania': scores[1],
                                'ciencias_naturales': scores[2],
                                'ingles': scores[3],
                                'lectura_critica': scores[4]
                            }
                            students.append(student_data)
                        
                        i = j
                    else:
                        i += 1
                else:
                    i += 1
    
    doc.close()
    return students

# Encontrar todos los archivos InformeGrupo
base_dir = "/workspace/RESULTADOS SIMULACROS I.E-IDEXUD"
all_students = []

print("=== ESCANEANDO TODOS LOS INFORMES GRUPALES ===\n")

for root, dirs, files in os.walk(base_dir):
    for file in files:
        if 'InformeGrupo' in file and file.endswith('.pdf'):
            pdf_path = os.path.join(root, file)
            students = extract_student_data_from_pdf(pdf_path)
            if students:
                print(f"{len(students):3d} estudiantes - {file}")
                all_students.extend(students)

print(f"\n{'='*60}")
print(f"TOTAL ESTUDIANTES PROCESADOS: {len(all_students)}")
print(f"{'='*60}\n")

# Crear DataFrame
if all_students:
    df = pd.DataFrame(all_students)
    
    # Reordenar columnas
    df = df[['institucion', 'nombre', 'grupo', 'matematicas', 'sociales_ciudadania', 
             'ciencias_naturales', 'ingles', 'lectura_critica']]
    
    # Guardar a Excel
    output_file = "/workspace/resultados_estudiantes_por_institucion.xlsx"
    df.to_excel(output_file, index=False)
    print(f"✅ Archivo Excel guardado en: {output_file}")
    
    # Mostrar resumen por institución
    print("\n" + "="*60)
    print("RESUMEN POR INSTITUCIÓN")
    print("="*60)
    summary = df.groupby('institucion').agg({
        'nombre': 'count',
        'matematicas': 'mean',
        'sociales_ciudadania': 'mean',
        'ciencias_naturales': 'mean',
        'ingles': 'mean',
        'lectura_critica': 'mean'
    }).round(2)
    summary.columns = ['Total Estudiantes', 'Prom Mat', 'Prom Soc', 'Prom Cien', 'Prom Ing', 'Prom Lect']
    summary = summary.sort_values('Total Estudiantes', ascending=False)
    print(summary.to_string())
    
    # Mostrar primeras filas
    print("\n" + "="*60)
    print("PRIMEROS REGISTROS DEL EXCEL")
    print("="*60)
    print(df.head(20).to_string(index=False))
