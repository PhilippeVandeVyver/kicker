import os
from azure.storage.blob import BlobServiceClient

LOCAL_HEATMAP_DIR = "app/static/heatmaps"
os.makedirs(LOCAL_HEATMAP_DIR, exist_ok=True)

AZURE_CONN_STR = os.getenv("AZURE_STORAGE_CONNECTION_STRING")
AZURE_CONTAINER = "heatmaps"

def save_heatmap_local( game_id, image_bytes):
    filename = f"game{game_id}.png"
    path = os.path.join(LOCAL_HEATMAP_DIR, filename)
    with open(path, "wb") as f:
        f.write(image_bytes)
    return f"/static/heatmaps/{filename}"

def upload_heatmap_blob(game_id, image_bytes):
    if not AZURE_CONN_STR:
        raise RuntimeError("Azure connection string not set")

    blob_service_client = BlobServiceClient.from_connection_string(AZURE_CONN_STR)
    container_client = blob_service_client.get_container_client(AZURE_CONTAINER)

    try:
        container_client.create_container()
    except Exception:
        pass

    filename = f"game{game_id}.png"
    blob_client = container_client.get_blob_client(filename)
    blob_client.upload_blob(image_bytes, overwrite=True)

    return blob_client.url
