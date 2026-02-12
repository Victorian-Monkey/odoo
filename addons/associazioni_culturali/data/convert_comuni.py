import csv
import os
import sys

# Script per convertire il CSV ISTAT dei comuni nel formato XML/CSV importabile in Odoo
# Fonte dati attesa: Elenco-comuni-italiani.csv (formato ISTAT standard)
# Encoding input: ISO-8859-1 (Latin1) o Windows-1252

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
INPUT_FILE = os.path.join(BASE_DIR, "Elenco-comuni-italiani.csv")
OUTPUT_FILE = os.path.join(BASE_DIR, "res.comune.csv")


def main():
    print(f"Reading {INPUT_FILE}...")

    try:
        # Usa encoding 'latin1' che è tollerante per i file ISTAT
        with (
            open(INPUT_FILE, "r", encoding="latin1", newline="") as f_in,
            open(OUTPUT_FILE, "w", encoding="utf-8", newline="") as f_out,
        ):
            reader = csv.reader(f_in, delimiter=";")
            writer = csv.writer(f_out, quoting=csv.QUOTE_NONNUMERIC)

            # Scrivi header Odoo
            # Campi: id (xml_id), name, codice_catastale, provincia, codice_istat, cap
            writer.writerow(
                ["id", "name", "codice_catastale", "provincia", "codice_istat", "cap"]
            )

            # Aggiungi record speciale per Estero
            writer.writerow(["comune_estero", "Estero", "Z000", "", "", ""])

            # Salta intestazione ISTAT
            try:
                header = next(reader)
            except StopIteration:
                print("Error: Empty input file")
                return

            count = 0
            for row in reader:
                # Salta righe vuote o malformate
                if not row or len(row) < 19:
                    continue

                try:
                    # Estrazione dati basata su colonne ISTAT standard
                    # 4: Codice Comune formato alfanumerico
                    # 5: Denominazione (Italiana e straniera)
                    # 6: Denominazione in italiano
                    # 14: Sigla automobilistica
                    # 19: Codice Catastale del comune

                    # Nome: usa denominazione italiano (6) se presente, altrimenti (5)
                    # Nota: alcuni file ISTAT hanno denominazione in colonna 5 e basta.
                    # Controlliamo se colonna 6 esiste ed è piena.
                    nome = row[5].strip()
                    if len(row) > 6 and row[6].strip():
                        nome = row[6].strip()

                    provincia = row[14].strip() if len(row) > 14 else ""
                    codice_istat = row[4].strip() if len(row) > 4 else ""
                    codice_catastale = row[19].strip() if len(row) > 19 else ""

                    # Se manca il codice catastale, salta (essenziale per ID e logica)
                    if not codice_catastale:
                        continue

                    # Genera ID univoco (External ID)
                    xml_id = f"comune_{codice_catastale}"

                    # Scrivi riga
                    writer.writerow(
                        [
                            xml_id,
                            nome,
                            codice_catastale,
                            provincia,
                            codice_istat,
                            "",  # CAP non disponibile nel file ISTAT standard
                        ]
                    )
                    count += 1

                except Exception as e:
                    print(f"Skipping row due to error: {e} - Row: {row}")
                    continue

            print(f"Successfully converted {count} municipalities to {OUTPUT_FILE}.")

    except FileNotFoundError:
        print(f"Error: File {INPUT_FILE} not found.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")


if __name__ == "__main__":
    main()
