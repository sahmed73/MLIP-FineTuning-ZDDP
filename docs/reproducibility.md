# Reproducing the figures

The [round-0 DFT structures and reference labels](../data/dft_round0/README.md) are included. The plotting script currently expects the original project checkout and its model predictions, which are not distributed; it does not fetch or upload anything. Install Python with ASE, NumPy and Matplotlib, then run:

```bash
MPLCONFIGDIR=/tmp/mlip-plot-cache python scripts/plot_results.py --project /path/to/ZDDP-AO_Synergy
```

The script generates PDF and PNG figures and a metrics JSON under `figures/`. It verifies test IDs, grouped split separation, atom ordering, coordinates and labels between paired predictions. Compare resulting metrics with the source project's saved results and independently review any figures before release. Validation-loss points are parsed from the training log; logged loss units reflect model normalization. Training loss is not currently plotted because a comparable epoch-level series has not been verified.

No model weights or OMol25 replay data are distributed here. The methodology describes the recorded run; it is not a claim that the complete training run can be reproduced without authorized access to the private dataset, model and appropriate dependencies.
