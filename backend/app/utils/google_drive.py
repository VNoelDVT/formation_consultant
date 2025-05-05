from backend.app.utils.auth import get_google_service

def upload_to_gdrive(file_path: str, file_name: str = None) -> str:
    service = get_google_service('drive', 'v3')

    if not file_name:
        file_name = file_path.split('/')[-1]

    file_metadata = {'name': file_name}
    media = MediaFileUpload(file_path, mimetype='image/png')

    uploaded_file = service.files().create(
        body=file_metadata,
        media_body=media,
        fields='id'
    ).execute()

    file_id = uploaded_file.get('id')

    # Rendre le fichier publicement accessible
    service.permissions().create(
        fileId=file_id,
        body={'role': 'reader', 'type': 'anyone'},
    ).execute()

    file_url = f"https://drive.google.com/uc?id={file_id}"
    return file_url
