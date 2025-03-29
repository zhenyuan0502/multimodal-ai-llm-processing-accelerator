import logging
from dotenv import load_dotenv
import os
import requests
import json
import sys

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s:%(levelname)s:%(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

# Reduce Azure SDK logging level
_logger = logging.getLogger("azure.core")
_logger.setLevel(logging.WARNING)

load_dotenv()

DOC_SAMPLES_JSON_PATH = "demo_files/doc_intel_processing_samples.json"
VIDEO_SAMPLES_JSON_PATH = "demo_files/content_understanding/video_file_web_links.json"
DOC_SAMPLES_DOWNLOAD_DIR = "demo_files/download/doc_intel_processing"
VIDEO_SAMPLES_DOWNLOAD_DIR = "demo_files/download/video_files"

### Load (and download) all required demo files.
def download_url_source_to_local(
    url_source: str, output_folder: str, save_name: str = None
) -> str:
    """
    Downloads a file from a URL source to a local path, returning the local
    path of the downloaded file.
    """
    # Download file to local path
    basename = os.path.basename(url_source).split("?")[0]
    if save_name:
        # Clean the save_name automatically
        accepted_chars = (
            "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-_ "
        )
        save_name = save_name.replace(" ", "_").replace("-", "_").lower()
        save_name = "".join([c for c in save_name if c in accepted_chars])
        ext = os.path.splitext(basename)[1]
        basename = f"{save_name}{ext}"
    local_path = os.path.join(output_folder, basename)
    if not os.path.exists(local_path):
        os.makedirs(output_folder, exist_ok=True)
        logging.info(f"Downloading {url_source} to {local_path}")
        response = requests.get(url_source)
        response.raise_for_status()
        with open(local_path, "wb") as f:
            f.write(response.content)
    # Return local path
    return local_path

def are_samples_downloaded(json_file_path: str, download_folder: str) -> bool:
    """
    Check if the sample files listed in a JSON file are downloaded.
    """
    with open(json_file_path, "r") as json_file:
        url_sources: dict[str, str] = json.load(json_file)
        
    for name in url_sources.keys():
        local_path = os.path.join(download_folder, name)
        if not os.path.exists(local_path):
            return False
        
    return True

def are_video_samples_downloaded() -> bool:
    return are_samples_downloaded(
        VIDEO_SAMPLES_JSON_PATH,
        VIDEO_SAMPLES_DOWNLOAD_DIR
    )
    
def are_doc_samples_downloaded() -> bool:
    return are_samples_downloaded(
        DOC_SAMPLES_JSON_PATH,
        DOC_SAMPLES_DOWNLOAD_DIR
    )

def download_doc_samples():
    with open(DOC_SAMPLES_JSON_PATH, "r") as json_file:
        doc_intel_url_sources: dict[str, str] = json.load(json_file)
        
    return [
        (
            name,
            download_url_source_to_local(
                url_source, DOC_SAMPLES_DOWNLOAD_DIR, name
            ),
        )
        for name, url_source in doc_intel_url_sources.items()
    ]
    
def download_video_samples():
    with open(VIDEO_SAMPLES_JSON_PATH, "r") as json_file:
        cu_video_file_url_sources: dict[str, str] = json.load(json_file)
        
    return [
    (
        name,
        download_url_source_to_local(url_source, VIDEO_SAMPLES_DOWNLOAD_DIR, name),
    )
    for name, url_source in cu_video_file_url_sources.items()
]
    
def download():
    doc_intel_tupples, video_file_tupples = [], []
    if not are_doc_samples_downloaded():
        logging.info('Downloading doc samples')
        doc_intel_tupples = download_doc_samples()
    else:
        logging.info('Doc samples already downloaded')
        doc_intel_tupples = [
            (
                os.path.splitext(os.path.basename(fn))[0],
                os.path.join(DOC_SAMPLES_DOWNLOAD_DIR, fn),
            )
            for fn in os.listdir(DOC_SAMPLES_DOWNLOAD_DIR)
            if fn.endswith((".pdf"))
        ]
        
    if not are_video_samples_downloaded():
        logging.info('Downloading video samples')
        video_file_tupples = download_video_samples()
    else:   
        logging.info('Video samples already downloaded')
        video_file_tupples = [
            (
                os.path.splitext(os.path.basename(fn))[0],
                os.path.join(VIDEO_SAMPLES_DOWNLOAD_DIR, fn),
            )
            for fn in os.listdir(VIDEO_SAMPLES_DOWNLOAD_DIR)
            if fn.endswith((".mp4"))
        ]
        
    return doc_intel_tupples, video_file_tupples
        

# To run download in CLI
if __name__ == "__main__":
    if len(sys.argv) > 1:
        function_name = sys.argv[1]
        if function_name in globals():
            globals()[function_name]()
        else:
            print(f"Function '{function_name}' not found.")