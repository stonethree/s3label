from backend.lib import data_upload as du


def test_hash_of_identical_files_in_different_folders_with_different_filenames_is_the_same():
    hash_1 = du.calculate_file_hash(r'test_images/image.jpg')
    hash_2 = du.calculate_file_hash(r'unit_test_data/image_copy.jpg')

    assert hash_1 == hash_2


def test_hash_of_different_files_is_different():
    hash_1 = du.calculate_file_hash(r'test_images/image.jpg')
    hash_2 = du.calculate_file_hash(r'test_images/image2.jpg')

    assert hash_1 != hash_2


def test_get_hash_returns_none_if_file_not_found():
    hash_1 = du.calculate_file_hash(r'test_images/imageABC.jpg')

    assert hash_1 is None


def test_get_images_in_folder_nonrecursive():
    im_paths = du.get_images_in_folder('test_images', recursive=False)

    assert len(im_paths) == 6
    assert im_paths[0] == r'test_images/froth_image.jpg'
    assert im_paths[1] == r'test_images/image.jpg'


def test_get_images_in_folder_recursive():
    im_paths = du.get_images_in_folder('test_images', recursive=True)

    assert len(im_paths) == 7
    assert im_paths[0] == r'test_images/another_folder/image_copy.jpg'
    assert im_paths[1] == r'test_images/froth_image.jpg'
    assert im_paths[2] == r'test_images/image.jpg'

