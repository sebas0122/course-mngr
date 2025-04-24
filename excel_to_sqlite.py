import sqlite3
import pandas as pd

def read_excel_file(file_path):
    try:
        df = pd.read_excel(file_path, sheet_name=None)
        print("Excel file read successfully!")
        return df
    except Exception as e:
        print(f"An error occurred: {e}")

excel_file = "data/DATOS_PERMANENCIA_ESTUDIANTIL.xlsx"
sheets = read_excel_file(excel_file)

sheet_columns = [
    'CODIGO_MATERIA',
    'MATERIA',
    'GRUPO',
    'MATRICULADOS_INICIO_SEMESTRE',
    'MATRICULADOS_FINAL_SEMESTRE',
    'CANCELARON',
    'PERDIO_MATERIA_UNA_VEZ',
    'PERDIO_MATERIA_DOS_VECES',
    'GANARON_A_LA_PRIMERA',
    'GANARON_A_LA_SEGUNDA',
    'GANARON_A_LA_TERCERA',
    'PERDIERON_A_LA_PRIMERA_VEZ',
    'SIN_NOTA',
    'INCOMPLETO',
    'PERDIERON_Y_YA_HABIAN_PERDIDO_UNA_VEZ_ANTES',
    'PERDIERON_Y_YA_HABIAN_PERDIDO_DOS_VECES_ANTES'
]

conn = sqlite3.connect('data/permanencia_est.db')
cursor = conn.cursor()

for sheet_name, df in sheets.items():
    # Clean up the sheet name to be a valid SQL identifier (remove spaces or special characters if needed)
    table_name = f'data_{sheet_name}'
    if sheet_name == "Resumen":
        continue

    # Create the table for this semester if it doesn't exist
    cursor.execute(f'''
    CREATE TABLE IF NOT EXISTS {table_name} (
        CODIGO_MATERIA INTEGER,
        MATERIA TEXT,
        GRUPO INTEGER,
        MATRICULADOS_INICIO_SEMESTRE INTEGER,
        MATRICULADOS_FINAL_SEMESTRE INTEGER,
        CANCELARON INTEGER,
        PERDIO_MATERIA_UNA_VEZ INTEGER,
        PERDIO_MATERIA_DOS_VECES INTEGER,
        GANARON_A_LA_PRIMERA INTEGER,
        GANARON_A_LA_SEGUNDA INTEGER,
        GANARON_A_LA_TERCERA INTEGER,
        PERDIERON_A_LA_PRIMERA_VEZ INTEGER,
        SIN_NOTA INTEGER,
        INCOMPLETO INTEGER,
        PERDIERON_Y_YA_HABIAN_PERDIDO_UNA_VEZ_ANTES INTEGER,
        PERDIERON_Y_YA_HABIAN_PERDIDO_DOS_VECES_ANTES INTEGER,

        PRIMARY KEY (CODIGO_MATERIA)
    );
    ''')

    conn.commit()

    for _, row in df.iterrows():

        values = tuple(row[col] for col in sheet_columns)

        cursor.execute(f'''
        INSERT OR REPLACE INTO {table_name} ({', '.join(sheet_columns)})
        VALUES ({', '.join(['?' for _ in sheet_columns])})
        ''', values)
    conn.commit()

# Close the connection
conn.close()