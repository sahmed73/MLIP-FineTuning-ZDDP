# MLIPs for ZDDP chemistry: benchmark, select, fine-tune

Machine-learned interatomic potentials (MLIPs) can enable molecular simulations at a scale beyond routine electronic-structure calculations. But a general-purpose potential can fail on stretched bonds and unusual electronic states relevant to lubricant additives. This project benchmarks MACE, UMA and eSEN against consistent density functional theory (DFT) references, selects a foundation model, and adapts it to zinc dialkyldithiophosphate (ZDDP) chemistry.

**Key result: fine-tuning UMA-S reduced held-out force RMSE by about 35% on 157 configurations.**

| Held-out metric | Pretrained UMA-S | Fine-tuned UMA-S | Reduction |
|---|---:|---:|---:|
| All-atom force-component RMSE (eV/Å) | 0.0340 | 0.0222 | 35% |
| Composition-centered energy RMSE (meV/atom) | 1.153 | 0.286 | 75% |

Force metrics pool 35,163 Cartesian components. Energy metrics use 154 configurations with repeated compositions, removing a mean offset separately for each composition and model. The grouped test split holds out configurations associated with scan points; every bond type remains represented in training. See [metric definitions](docs/evaluation.md) and [machine-readable results](figures/metrics.json).

![Fine-tuning force parity](figures/heldout_force_parity.png)
*Pretrained and fine-tuned UMA-S evaluated on identical held-out configurations. Metrics pool all Cartesian force components; structures contribute in proportion to their number of atoms.*

## My research role and skills

This portfolio presents my ongoing research on adapting foundation MLIPs to ZDDP chemistry. My work spans preparing and checking DFT reference data, comparing model families, fine-tuning UMA-S with replay, and evaluating accuracy, generalization and molecular-dynamics stability. The released materials document the data and evaluation workflow; the original foundation models and training frameworks are third-party tools.

**Skills demonstrated:** Python, NumPy, ASE, ORCA/DFT, MACE, UMA/fairchem, eSEN, transfer learning, grouped dataset splitting, HPC/Slurm workflows and scientific visualization.

## Research workflow

```mermaid
flowchart LR
    A["Sample molecular structures<br/>and targeted bond stretches"] --> B["DFT labels<br/>energies, forces and quality checks"]
    B --> C["Benchmark<br/>MACE · UMA · eSEN"]
    C --> D["Select UMA-S<br/>using task-specific criteria"]
    D --> E["Fine-tune with replay<br/>grouped train / validation / test"]
    E --> F["Evaluate<br/>held-out accuracy, forgetting and stability"]
```

The release contains 651 project-specific DFT configurations and test predictions for all three foundation-model families plus the fine-tuned UMA-S model. Start with the [DFT dataset and production workflow](data/dft_round0/README.md), [example notebook](examples/inspect_dft.ipynb), or [standalone plotting instructions](docs/reproducibility.md).

## Foundation-model comparison

![Foundation model force comparison](figures/foundation_force_parity.png)
*Zero-shot comparison. Force parity includes all Cartesian components of all atoms in the scored benchmark structures. These data informed model selection; they are not an independent test of a fine-tuned model.*

## Model selection

The benchmark used ORCA ωB97M-V/def2-TZVPD labels following OMol25 settings. It assessed forces, relative energies, conformers, binding curves and reaction energies. UMA-S 1.2.1 and eSEN-sm conserving met all five defined targets; MACE-OMOL-0 met four. UMA-S was selected for fine-tuning based on the broader benchmark, including stretched-bond behavior and practical simulation performance. This is a task-specific selection, not a general ranking of the model families.

## Targeted adaptation

Targeted bond-stretch and finite-temperature configurations were added to the reference set. Related scan-point structures were grouped before splitting: 404 training, 90 validation and 157 test structures in the round-0 refit. The test contains unseen groups, **not unseen bond types**. UMA-S was fully fine-tuned from the pretrained OMol head with replay from OMol25, intended to reduce loss of general chemical knowledge. The refit used a learning rate of 10⁻⁴, batch size 4 and 10 epochs.

![Held-out relative energy comparison](figures/heldout_energy_parity.png)
*Per-atom energies are centered separately for each chemical composition and model on the test set. This evaluates relative variation within composition, not absolute energies; singleton compositions are excluded. See [evaluation](docs/evaluation.md).*

![Held-out error distributions](figures/heldout_errors.png)
*Errors on the same test configurations. Force histogram is restricted to ±0.3 eV/Å for readability; tails exist outside the displayed range.*

## What the results mean—and what they do not

The held-out force comparison measures how well the model reproduces local DFT forces on this distribution; it does not establish reaction kinetics or transferability to all ZDDP chemistries. Several stretched C–O configurations remain challenging after fine-tuning, and independent general-domain checks show energy drift, especially for radicals, despite replay. The DFT reference itself can have limitations for condensed-phase properties. Related geometries within a chemistry family and compositional centering further constrain generalization claims.

## Reproduce and audit

See [DFT dataset and calculation workflow](data/dft_round0/README.md), [methodology](docs/methodology.md), [evaluation](docs/evaluation.md), and [reproducibility](docs/reproducibility.md). Reference energies, forces, splits and held-out model predictions are included. Run `python scripts/plot_results.py --out reproduced_figures` to recreate the figures.

![Validation loss](figures/validation_loss.png)
*Validation loss as recorded during training; the horizontal axis counts validation evaluations, which occur more than once per epoch. Normalized logged loss is not a physical error metric. A comparable training-loss series has not yet been verified.*
