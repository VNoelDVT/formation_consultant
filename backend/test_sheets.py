from app.agents.sheets_tool import create_new_sheet, write_prices_to_sheet

if __name__ == '__main__':
    # 1️⃣ Créer une nouvelle feuille
    title = 'Demo Auto Sheet'
    spreadsheet_id, first_sheet_name = create_new_sheet(title)

    # 2️⃣ Données à écrire
    data = [
        ['Marque', 'Prix'],
        ['Lenovo', '1000'],
        ['Dell', '1200'],
        ['HP', '900']
    ]

    # 3️⃣ Ecrire dedans
    response = write_prices_to_sheet(spreadsheet_id, first_sheet_name, data)
    print("✅ Données écrites :", response)
