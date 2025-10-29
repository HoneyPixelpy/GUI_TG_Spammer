import asyncio
import shutil
import os

from loguru import logger

from settings import BASE_DIR


@logger.catch
async def count_images(
    file_path: str = BASE_DIR / "photos"
    ) -> int:
    """
    Возвращает количество файлов в директории.
    """
    files = os.listdir(file_path)
    return len(files)

@logger.catch
async def delete_all_files_in_path(
    directorys: list[str] = [
        "photos",
        "archive",
        ]
    ) -> str:
    """
    Удаляем все файлы в дирректории.
    """
    # Получаем список файлов в указанной директории
    for dir in directorys:
        directory = BASE_DIR / dir
        if not directory.exists():
            continue

        files = os.listdir(directory)
        tasks = []
        for file in files:
            file_path = directory / file
            if file_path.is_file():
                tasks.append(asyncio.to_thread(os.remove, file_path))
            elif file_path.is_dir():
                tasks.append(asyncio.to_thread(shutil.rmtree, file_path))
        
        await asyncio.gather(*tasks)

@logger.catch
async def get_history_files(
    directory: list[str] = "archive",
    ) -> dict:
    """
    Получаем пути к каждому файлу с историей сообщений в archive.
    """
    dict_files = {}
    files = os.listdir(directory)
    for file in files:
        file_path = os.path.join(BASE_DIR, "archive/"+file)
        dict_files[file] = file_path
    return dict_files

