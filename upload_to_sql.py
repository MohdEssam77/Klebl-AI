import pyodbc
import json

def create_tables(cursor):
    # Create Plankopf table
    cursor.execute("""
        CREATE TABLE Plankopf (
            Planschlüssel NVARCHAR(50),
            Stat_Pos NVARCHAR(50),
            Auftr_Nr NVARCHAR(50),
            Index NVARCHAR(10),
            Fertigteil_Position NVARCHAR(100),
            Stück INT,
            Volumen_m3 FLOAT,
            Gewicht_to FLOAT
        )
    """)

    # Create Vorderansicht table
    cursor.execute("""
        CREATE TABLE Vorderansicht (
            Länge_Gesamt FLOAT,
            Höhe_Gesamt FLOAT,
            Ausklinkung_links_Länge FLOAT,
            Ausklinkung_links_Höhe FLOAT,
            Ausklinkung_rechts_Länge FLOAT,
            Ausklinkung_rechts_Höhe FLOAT
        )
    """)

    # Create Seitenansicht table
    cursor.execute("""
        CREATE TABLE Seitenansicht (
            Breite FLOAT
        )
    """)

    # Create Liste_Stahl table
    cursor.execute("""
        CREATE TABLE Liste_Stahl (
            Pos INT,
            Anzahl INT,
            Durchmesser INT,
            Länge FLOAT,
            Bemerkung NVARCHAR(200)
        )
    """)

    # Create Liste_Einbauteile table
    cursor.execute("""
        CREATE TABLE Liste_Einbauteile (
            Pos NVARCHAR(10),
            Stck INT,
            Bezeichnung NVARCHAR(200)
        )
    """)

def insert_data(cursor, data):
    # Insert Plankopf data
    plankopf = data['Plankopf']
    cursor.execute("""
        INSERT INTO Plankopf VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        plankopf['Planschlüssel'],
        plankopf['Stat.Pos'],
        plankopf['Auftr. Nr'],
        plankopf['Index'],
        plankopf['Fertigteil Position'],
        plankopf['Stück'],
        plankopf['Volumen (m3)'],
        plankopf['Gewicht (to)']
    ))

    # Insert Vorderansicht data
    vorderansicht = data['Vorderansicht']
    cursor.execute("""
        INSERT INTO Vorderansicht VALUES (?, ?, ?, ?, ?, ?)
    """, (
        vorderansicht['Bauteil']['Länge_Gesamt'],
        vorderansicht['Bauteil']['Höhe_Gesamt'],
        vorderansicht['Ausklinkung_links']['Länge'],
        vorderansicht['Ausklinkung_links']['Höhe'],
        vorderansicht['Ausklinkung_rechts']['Länge'],
        vorderansicht['Ausklinkung_rechts']['Höhe']
    ))

    # Insert Seitenansicht data
    cursor.execute("""
        INSERT INTO Seitenansicht VALUES (?)
    """, (data['Seitenansicht_Draufsicht']['Bauteil']['Breite'],))

    # Insert Liste_Stahl data
    for item in data['Liste_Stahl']:
        cursor.execute("""
            INSERT INTO Liste_Stahl VALUES (?, ?, ?, ?, ?)
        """, (
            item['Pos'],
            item['Anzahl'],
            item['Ø'],
            item['Länge'],
            item['Bemerkung']
        ))

    # Insert Liste_Einbauteile data
    for item in data['Liste_Einbauteile']:
        cursor.execute("""
            INSERT INTO Liste_Einbauteile VALUES (?, ?, ?)
        """, (
            item['Pos'],
            item['Stck'],
            item['Bezeichnung']
        ))

def main():
    # Connection string - replace with your details
    conn_str = (
        "Server=localhost\SQLEXPRESS;Database=master;Trusted_Connection=True;"
    )
    
    
    # Read JSON data
    with open('your_data.json', 'r', encoding='utf-8') as f:
        data = json.load(f)

    # Connect to database and perform operations
    conn = pyodbc.connect(conn_str)
    cursor = conn.cursor()

    try:
        create_tables(cursor)
        insert_data(cursor, data)
        conn.commit()
        print("Data successfully uploaded to MSSQL")
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    main()
