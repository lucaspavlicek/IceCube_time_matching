from src.paths import *            

runs = ['run_0000023', 'run_0000024', 'run_0000025']

for d in [1, 2, 3]:

    for c in [1, 2, 3, 4, 5, 6, 7, 8]:

        indices = []

        with open(ICECUBE_PASS2_DIR / f'y2023m12d2{d}-IceCube-pass2' / f'y2023m12d2{d}-IceCube-pass2.csv', 'r') as f:
            next(f)
            for i, line in enumerate(f, start=1):
                if i % 10 == 0:
                    indices.append(int(line.split(',')[c-1]))

        in_path = ICECUBE_DATA_DIR / f'{runs[d-1]}_2023122{d}' / runs[d-1] / f'{runs[d-1]}_chan-{c}_alldata.txt'
        out_path = MOCK_ICECUBE_DATA_DIR / f'run_999999{d}_0001010{d}' / f'run_999999{d}/run_999999{d}_chan-{c}_alldata.txt'

        out_path.parent.mkdir(parents=True, exist_ok=True)
            
        with open(in_path, 'r') as fr:
            with open(out_path, 'w') as fw:
                for j, line in enumerate(fr):

                    if j % 500 == 0 or j in indices:
                        fw.write(line)

