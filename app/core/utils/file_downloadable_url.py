from typing import List, Dict, Any

from data.repository import file_repository


async def generate_downloadable_urls(files: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Takes a list of dicts containing 'file_url', generates presigned URLs for each,
    and returns a new list with updated 'file_url'.
    """
    updated_files = []
    for file in files:
        file_url = file.get("file_url")
        if file_url:
            downloadable = await file_repository.get_download_url(file_url)
            updated_files.append({**file, "file_url": downloadable})
        else:
            updated_files.append(file)
    return updated_files
