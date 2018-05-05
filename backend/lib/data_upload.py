import pathlib
import hashlib
import glob
import os


def calculate_file_hash(file_path):
    """
    Calculate the hash of a file on disk.

    We store a hash of the file in the database, so that we can keep track of files if they are ever moved to new
    drives.

    :param file_path:
    :return:
    """

    block_size = 65536
    hasher = hashlib.sha1()

    p = pathlib.Path(file_path)

    if p.exists():
        with p.open('rb') as f:
            buf = f.read(block_size)
            while len(buf) > 0:
                hasher.update(buf)
                buf = f.read(block_size)

        return hasher.hexdigest()
    else:
        return None


def get_images_in_folder(folder, recursive=False):
    """
    Get a list of file paths of images in a folder. Choose whether to search recursively for paths recursively.

    :param folder:
    :param recursive: if True, search for images recursively
    :return:
    """

    if recursive:
        image_paths = glob.glob(os.path.join(folder, '**/*.jpeg'), recursive=True)
        image_paths.extend(glob.glob(os.path.join(folder, '**/*.jpg'), recursive=True))
        image_paths.extend(glob.glob(os.path.join(folder, '**/*.png'), recursive=True))
        image_paths.extend(glob.glob(os.path.join(folder, '**/*.bmp'), recursive=True))
    else:
        image_paths = glob.glob(os.path.join(folder, '*.jpeg'), recursive=False)
        image_paths.extend(glob.glob(os.path.join(folder, '*.jpg'), recursive=False))
        image_paths.extend(glob.glob(os.path.join(folder, '*.png'), recursive=False))
        image_paths.extend(glob.glob(os.path.join(folder, '*.bmp'), recursive=False))

    # convert to forward slashes
    image_paths = [p.replace('\\', '/') for p in image_paths]

    return sorted(image_paths)
