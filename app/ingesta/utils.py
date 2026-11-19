import glob
import os
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def encontrar_zip():
    data_dir = os.path.join(BASE_DIR, 'data')
    zips = glob.glob(os.path.join(data_dir, '*.zip'))
    if not zips:
        return None
    return max(zips, key=os.path.getmtime)


if __name__ == '__main__':
    print(encontrar_zip())