from backend.app.utils.auth import get_google_service

def create_new_sheet(title):
    """
    Crée une nouvelle feuille Google Sheets avec le titre donné.
    Retourne l'ID du Spreadsheet.
    """
    service = get_google_service('sheets', 'v4')
    spreadsheet = {
        'properties': {
            'title': title
        }
    }
    sheet = service.spreadsheets().create(body=spreadsheet).execute()
    spreadsheet_id = sheet.get('spreadsheetId')

    # Récupère le nom réel de la première feuille
    first_sheet_name = sheet['sheets'][0]['properties']['title']
    print(f"✅ Nouvelle feuille créée avec ID : {spreadsheet_id}, première feuille : {first_sheet_name}")
    return spreadsheet_id, first_sheet_name


def write_prices_to_sheet(spreadsheet_id, sheet_name, data):
    """
    Ecrit des données dans la feuille spécifiée.
    """
    service = get_google_service('sheets', 'v4')
    sheet = service.spreadsheets()

    range_name = f'{sheet_name}!A1'

    request = sheet.values().update(
        spreadsheetId=spreadsheet_id,
        range=range_name,
        valueInputOption='RAW',
        body={'values': data}
    )
    response = request.execute()
    return response
