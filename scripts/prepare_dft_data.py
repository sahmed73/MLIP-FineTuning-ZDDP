#!/usr/bin/env python3
"""Extract the project DFT references corresponding to the recorded round-0 split."""
import argparse, csv, hashlib, json
from pathlib import Path
import numpy as np
from ase.io import iread, write

p=argparse.ArgumentParser(); p.add_argument('--predictions',type=Path,required=True); p.add_argument('--splits',type=Path,required=True); p.add_argument('--out',type=Path,default=Path('data/dft_round0')); args=p.parse_args()
with args.splits.open() as f: rows=list(csv.DictReader(f))
lookup={r['calc_id']:r for r in rows}; assert len(lookup)==len(rows)
result={k:[] for k in ('train','val','test')}; seen=set()
for atom in iread(args.predictions,index=':'):
 cid=atom.info['calc_id']
 if cid not in lookup: continue
 assert cid not in seen; seen.add(cid); row=lookup[cid]
 assert len(atom)==int(row['n_atoms']) and np.isfinite(atom.info['REF_energy']) and np.isfinite(atom.arrays['REF_forces']).all() and np.isfinite(atom.positions).all()
 # Do not include any MLIP predictions or training-only metadata.
 atom.info={k:atom.info[k] for k in ('calc_id','config_type','charge','spin','REF_energy')}
 atom.info['group']=row['group']; atom.info['split']=row['split']
 for key in list(atom.arrays):
  if key not in ('numbers','positions','REF_forces'): del atom.arrays[key]
 result[row['split']].append(atom)
assert seen==set(lookup), (len(seen),len(lookup))
assert {k:len(v) for k,v in result.items()}=={'train':404,'val':90,'test':157}
groups={s:{a.info['group'] for a in frames} for s,frames in result.items()}
assert not (groups['train']&groups['val'] or groups['train']&groups['test'] or groups['val']&groups['test'])
args.out.mkdir(parents=True,exist_ok=True)
for split,frames in result.items():
 frames.sort(key=lambda a:a.info['calc_id']); write(args.out/f'{split}.extxyz',frames,format='extxyz')
with (args.out/'splits.csv').open('w',newline='') as f:
 w=csv.DictWriter(f,fieldnames=['calc_id','set','group','split','n_atoms','charge','spin']); w.writeheader(); w.writerows([{k:r[k] for k in w.fieldnames} for r in rows])
files=sorted(args.out.glob('*.extxyz'))+[args.out/'splits.csv']
(args.out/'SHA256SUMS').write_text(''.join(f'{hashlib.sha256(path.read_bytes()).hexdigest()}  {path.name}\n' for path in files))
print(json.dumps({k:len(v) for k,v in result.items()}))
