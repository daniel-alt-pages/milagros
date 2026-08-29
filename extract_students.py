import pymupdf
import os
import re
import pandas as pd
from pathlib import Path

def extract_text_from_pdf(pdf_path):
    """Extract text from a PDF file."""
    try:
        doc = pymupdf.open(pdf_path)
        text = ""
        for page in doc:
            text += page.get_text()
        doc.close()
        return text
    except Exception as e:
        print(f"Error reading {pdf_path}: {e}")
        return None

def parse_student_data(text, institution_from_path):
    """Parse student data from extracted text."""
    students = []
    
    if not text:
        return students
    
    # Split by "REPORTE INDIVIDUAL" which seems to mark each student
    student_sections = re.split(r'REPORTE INDIVIDUAL', text)
    
    for section in student_sections[1:]:  # Skip first empty section
        student = {}
        
        # Extract name - appears after the title and before "CÓDIGO ESTUDIANTE"
        name_match = re.search(r'MÓDULOS COMPETENCIAS GENÉRICAS\s*\n?\s*ICFES\s*\n?([A-ZÁÉÍÓÚÑÜ\. ]+?)\s*\.?\s*\n?\s*CÓDIGO ESTUDIANTE:', section, re.IGNORECASE)
        if name_match:
            name = name_match.group(1).strip()
            # Clean up the name - remove extra newlines and spaces
            name = re.sub(r'\s+', ' ', name)
            student['nombre'] = name
        
        # Extract Código Estudiante
        codigo_match = re.search(r'CÓDIGO ESTUDIANTE:\s*(\d+)', section, re.IGNORECASE)
        if codigo_match:
            student['codigo_estudiante'] = codigo_match.group(1)
        
        # Extract Institución desde el PDF
        inst_match = re.search(r'INSTITUCIÓN:\s*([^\n]+)', section, re.IGNORECASE)
        if inst_match:
            student['institucion'] = inst_match.group(1).strip()
        else:
            student['institucion'] = institution_from_path
        
        # Extract Nombre de la Prueba
        prueba_match = re.search(r'NOMBRE DE LA PRUEBA:\s*([^\n]+)', section, re.IGNORECASE)
        if prueba_match:
            student['prueba'] = prueba_match.group(1).strip()
        
        # Extract Fecha
        fecha_match = re.search(r'FECHA DE LA PRUEBA:\s*(\d+/\d+/\d+)', section, re.IGNORECASE)
        if fecha_match:
            student['fecha'] = fecha_match.group(1)
        
        # Extraer puntajes por materia - buscar patrones específicos
        # El formato parece ser: NOMBRE MATERIA\nPUNTAJE
        
        # Lectura Crítica
        lectura_match = re.search(r'LECTURA CRÍTICA\s*\n?\s*(\d+)', section)
        if not lectura_match:
            lectura_match = re.search(r'LECTURA\s*\n?\s*CRÍTICA\s*\n?\s*(\d+)', section)
        if lectura_match:
            student['lectura_critica'] = lectura_match.group(1)
        
        # Matemáticas
        matematicas_match = re.search(r'MATEMÁTICAS\s*\n?\s*(\d+)', section)
        if not matematicas_match:
            matematicas_match = re.search(r'MATEM\s*\n?\s*(\d+)', section)
        if matematicas_match:
            student['matematicas'] = matematicas_match.group(1)
        
        # Ciencias Naturales
        ciencias_match = re.search(r'CIENCIAS NATURALES\s*\n?\s*(\d+)', section)
        if not ciencias_match:
            ciencias_match = re.search(r'CIENCIAS\s*\n?\s*NATURALES\s*\n?\s*(\d+)', section)
        if ciencias_match:
            student['ciencias_naturales'] = ciencias_match.group(1)
        
        # Sociales y Ciudadanas
        sociales_match = re.search(r'SOCIALES Y CIUDADANAS\s*\n?\s*(\d+)', section)
        if not sociales_match:
            sociales_match = re.search(r'SOCIALES\s*\n?\s*y\s*\n?\s*CIUDADANAS\s*\n?\s*(\d+)', section)
        if sociales_match:
            student['sociales'] = sociales_match.group(1)
        
        # Inglés
        ingles_match = re.search(r'INGLÉS\s*\n?\s*(\d+)', section)
        if not ingles_match:
            ingles_match = re.search(r'INGLES\s*\n?\s*(\d+)', section)
        if ingles_match:
            student['ingles'] = ingles_match.group(1)
        
        # Puntaje Global
        global_match = re.search(r'PUNTAJE GLOBAL\s*\n?\s*(\d+)', section, re.IGNORECASE)
        if global_match:
            student['puntaje_global'] = global_match.group(1)
        
        # Percentiles - buscar números después de cada materia o global
        # El formato parece ser: percentil │\n100
        percentil_pattern = r'(\d+)\s*│\s*100'
        percentil_matches = re.findall(percentil_pattern, section)
        
        if percentil_matches:
            # Asumimos que el primer percentil es el global si hay varios
            student['percentil_global'] = percentil_matches[0]
        
        # Only add if we found a name
        if 'nombre' in student and student['nombre']:
            students.append(student)
    
    return students

def get_institution_from_path(filepath):
    """Extract institution name from file path."""
    parts = filepath.split(os.sep)
    for part in parts:
        if 'I.E' in part:
            return part.replace('Resul.Sim ', '').replace('Resul.Simu ', '').replace('Resultados Simulacro-', '').replace('RESULTADOS SIMULACROS I.E-IDEXUD/', '').strip()
    return "Unknown"

def main():
    all_students = []
    
    # Find all individual result PDFs
    pdf_files = []
    for root, dirs, files in os.walk('/workspace'):
        for file in files:
            if file.endswith('.pdf') and ('Resul.Indiv' in file or 'Resul.indiv' in file or 'Resul.Individu' in file or 'Resul.Individuales' in file):
                pdf_files.append(os.path.join(root, file))
    
    print(f"Found {len(pdf_files)} individual result PDFs")
    
    for pdf_path in pdf_files:
        print(f"Processing: {os.path.basename(pdf_path)}")
        institution = get_institution_from_path(pdf_path)
        text = extract_text_from_pdf(pdf_path)
        
        if text:
            students = parse_student_data(text, institution)
            all_students.extend(students)
            print(f"  -> Found {len(students)} students")
    
    if all_students:
        df = pd.DataFrame(all_students)
        
        # Reorder columns
        preferred_order = ['institucion', 'nombre', 'codigo_estudiante', 'prueba', 'fecha', 
                          'puntaje_global', 'percentil_global', 'lectura_critica', 
                          'matematicas', 'ciencias_naturales', 'sociales', 'ingles']
        
        # Only keep columns that exist
        existing_cols = [col for col in preferred_order if col in df.columns]
        other_cols = [col for col in df.columns if col not in preferred_order]
        df = df[existing_cols + other_cols]
        
        # Save to Excel
        output_path = '/workspace/resultados_estudiantes_por_institucion.xlsx'
        df.to_excel(output_path, index=False)
        print(f"\n✅ Saved {len(df)} students to {output_path}")
        print("\nColumns:", df.columns.tolist())
        print("\nFirst 10 rows:")
        pd.set_option('display.max_columns', None)
        pd.set_option('display.width', None)
        print(df.head(10).to_string())
        
        # Show institutions summary
        print("\n📊 Summary by Institution:")
        print(df.groupby('institucion').size().to_string())
    else:
        print("❌ No student data found.")

if __name__ == "__main__":
    main()
