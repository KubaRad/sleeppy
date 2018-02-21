import sys
import os

if __name__ == '__main__':
    with open(sys.argv[1]) as fin:
        catalogs = fin.readlines()
    catalog_names = [x.replace('\r', '').replace('\n', '') for x in catalogs ]

    with open(sys.argv[2]) as fin:
        file_names = fin.readlines()
    file_names = [x.replace('\r', '').replace('\n', '').replace('\t','')+'.SIG' for x in file_names ]

    catalog_content = {}
    for c in catalog_names:
        catalog_content[c] = [f.upper() for f in os.listdir(c) if (os.path.splitext(f)[1]).upper() == '.SIG' and os.path.isfile(os.path.join(c, f))]

    def find_catalog_fname(fn):
        for c in catalog_content:
            if fn in catalog_content[c]:
                return c
        return None

    for f in file_names:
        catalog = find_catalog_fname(f)
        if catalog is None:
            print('File {} Not found!!!!'.format(f))
        else:
            print(os.path.join(catalog,f), 'E:\\Schwarzer\\EXPORT-CPAP', 'ECG')
