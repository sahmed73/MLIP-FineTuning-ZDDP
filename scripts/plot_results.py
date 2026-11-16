#!/usr/bin/env python3
"""Reproduce figures using released reference and prediction data."""
import argparse, csv, json
from collections import defaultdict
from pathlib import Path
import numpy as np
from ase.io import iread
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

p=argparse.ArgumentParser(); p.add_argument('--data',type=Path,default=Path('data')); p.add_argument('--out',type=Path,default=Path('figures')); a=p.parse_args()
v=a.data/'predictions'; f=a.data/'dft_round0'
a.out.mkdir(parents=True,exist_ok=True)
plt.rcParams.update({'font.sans-serif':['Arial','DejaVu Sans'],'font.size':10,'axes.spines.top':False,'axes.spines.right':False,'pdf.fonttype':42,'figure.constrained_layout.use':True})
colors=['#526171','#007e87','#d08b36']; labels=['MACE-OMOL-0','UMA-S','eSEN-sm']; names=['mace-omol-0','uma-s-1p2p1-omol','esen-sm-conserving-omol']
def save(fig,name):
 for ext in ('pdf','png'): fig.savefig(a.out/f'{name}.{ext}',dpi=250)
 plt.close(fig)
def metrics(x,y):
 d=y-x; den=np.sum((x-x.mean())**2)
 return np.sqrt(np.mean(d*d)),np.mean(abs(d)),1-np.sum(d*d)/den if den else float('nan')
def parity(ax,x,y,title,color,unit):
 rm,ma,r2=metrics(x,y); ax.scatter(x,y,s=2,alpha=.20,color=color,rasterized=True); lo=min(x.min(),y.min()); hi=max(x.max(),y.max()); ax.plot([lo,hi],[lo,hi],color='black',lw=.8,ls='--'); ax.set(xlabel=f'DFT ({unit})',ylabel=f'MLIP ({unit})',title=title); ax.text(.04,.96,f'RMSE {rm:.3f}\nMAE {ma:.3f}\nR² {r2:.5f}',transform=ax.transAxes,va='top',bbox={'facecolor':'white','alpha':.8,'edgecolor':'none'}); return [float(rm),float(ma),float(r2)]
points=np.load(v/'benchmark_force_components.npz'); fig,axs=plt.subplots(1,3,figsize=(11,3.8)); scores={}
for ax,name,label,color in zip(axs,names,labels,colors): scores[label]=parity(ax,points[name+'__ref'],points[name+'__mlip'],label,color,'eV/Å')
save(fig,'foundation_force_parity')
with (f/'splits.csv').open() as fh: rows=list(csv.DictReader(fh))
test={r['calc_id'] for r in rows if r['split']=='test'}; train={r['group'] for r in rows if r['split']=='train'}; testgroups={r['group'] for r in rows if r['split']=='test'}
assert not train & testgroups
paths=[v/'uma-s-1p2p1-omol_test.extxyz',v/'uma-s-finetuned_test.extxyz']; data=[]
for path in paths:
 found={}
 for at in iread(path,index=':'):
  cid=at.info['calc_id']
  if cid in test:
   assert cid not in found; found[cid]=at
 assert set(found)==test,(path,len(found),len(test)); data.append(found)
ids=sorted(test); x=[]; ys=[[],[]]; groups=defaultdict(list)
for cid in ids:
 b,t=(d[cid] for d in data)
 assert np.array_equal(b.numbers,t.numbers) and np.allclose(b.positions,t.positions,atol=1e-7) and np.allclose(b.arrays['REF_forces'],t.arrays['REF_forces'],atol=1e-7) and np.isclose(b.info['REF_energy'],t.info['REF_energy'],atol=1e-7,rtol=0)
 x.extend(b.arrays['REF_forces'].ravel())
 for j,at in enumerate((b,t)): ys[j].extend(at.arrays['MLIP_forces'].ravel())
 groups[b.get_chemical_formula()].append(cid)
x=np.array(x); ys=[np.array(y) for y in ys]
fig,axs=plt.subplots(1,2,figsize=(8,3.8)); fs={}
for ax,y,label,color in zip(axs,ys,['Pretrained UMA-S','Fine-tuned UMA-S'],[colors[0],colors[1]]): fs[label]=parity(ax,x,y,label,color,'eV/Å')
save(fig,'heldout_force_parity')
# For each composition, independently center reference and predicted energies per atom.
# This removes composition-specific offsets on this evaluation set and is not absolute-energy accuracy.
energy=[]
for model in data:
 ref=[]; pred=[]
 for members in groups.values():
  if len(members)<2: continue
  rr=np.array([model[c].info['REF_energy']/len(model[c])*1000 for c in members]); pp=np.array([model[c].info['MLIP_energy']/len(model[c])*1000 for c in members]); ref.extend(rr-rr.mean()); pred.extend(pp-pp.mean())
 energy.append((np.array(ref),np.array(pred)))
fig,axs=plt.subplots(1,2,figsize=(8,3.8)); es={}
for ax,(ref,pred),label,color in zip(axs,energy,['Pretrained UMA-S','Fine-tuned UMA-S'],[colors[0],colors[1]]): es[label]=parity(ax,ref,pred,label,color,'meV/atom')
save(fig,'heldout_energy_parity')
fig,axs=plt.subplots(1,2,figsize=(8,3.5))
for y,label,color in zip(ys,['Pretrained','Fine-tuned'],[colors[0],colors[1]]): axs[0].hist(y-x,bins=np.linspace(-.3,.3,101),histtype='step',density=True,label=label,color=color)
for (ref,pred),label,color in zip(energy,['Pretrained','Fine-tuned'],[colors[0],colors[1]]): axs[1].hist(pred-ref,bins=60,histtype='step',density=True,label=label,color=color)
axs[0].set(xlabel='Force error (eV/Å)',ylabel='Density',title='Cartesian components'); axs[1].set(xlabel='Centered energy error (meV/atom)',ylabel='Density',title='Same-composition energies'); axs[0].legend(frameon=False); axs[1].legend(frameon=False); save(fig,'heldout_errors')
vals=json.loads((v/'validation_loss.json').read_text())
if vals:
 fig,ax=plt.subplots(figsize=(5,3)); ax.plot(np.arange(1,len(vals)+1),vals,marker='o',color=colors[1]); ax.set(xlabel='Validation evaluation index',ylabel='Validation loss (logged units)'); save(fig,'validation_loss')
(a.out/'metrics.json').write_text(json.dumps({'test_structures':len(test),'test_force_components':len(x),'foundation_force_parity_rmse_mae_r2':scores,'test_force_rmse_mae_r2':fs,'test_centered_energy_rmse_mae_r2':es,'energy_structures_used':len(energy[0][0]),'validation_points':len(vals)},indent=2)+'\n')
print((a.out/'metrics.json').read_text())
