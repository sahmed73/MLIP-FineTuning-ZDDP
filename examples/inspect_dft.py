"""Inspect a released test structure and independently compute force RMSE."""
from pathlib import Path
import numpy as np
from ase.io import read
root = Path(__file__).resolve().parents[1]
frames = read(root / 'data/dft_round0/test.extxyz', ':')
a = frames[0]
print('Test structures:', len(frames))
print('First ID:', a.info['calc_id'])
print('Energy (eV):', a.info['REF_energy'])
print('Force shape:', a.arrays['REF_forces'].shape)
pred = read(root / 'data/predictions/uma-s-finetuned_test.extxyz', ':')
by_id = {a.info['calc_id']: a for a in pred}
errors = []
for a in frames:
    b = by_id[a.info['calc_id']]
    assert np.allclose(a.arrays['REF_forces'], b.arrays['REF_forces'], atol=1e-7)
    errors.extend((b.arrays['MLIP_forces'] - a.arrays['REF_forces']).ravel())
print('Fine-tuned all-atom force component RMSE (eV/Å):', np.sqrt(np.mean(np.square(errors))))
