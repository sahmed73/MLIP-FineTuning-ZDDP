# Reproduce the figures

The repository includes the round-0 DFT labels, held-out predictions, benchmark force components and recorded validation loss. With Python 3, install `pip install -r requirements.txt` and run from the repository root:

```bash
python scripts/plot_results.py --out reproduced_figures
```

This regenerates the parity plots, error distributions, validation curve and `metrics.json` without access to the original project. Compare the metrics against `figures/metrics.json`. Definitions and limitations are in [evaluation.md](evaluation.md); data production and split details are in the [DFT dataset README](../data/dft_round0/README.md). Test predictions are documented [here](../data/predictions/README.md). ASE can read the `.extxyz` files; `examples/inspect_dft.py` provides a minimal example.

No model weights, ORCA software, custom basis file, complete original inputs/outputs or OMol25 replay data are distributed. The example ORCA input is a template, not a complete runnable reproduction. Reproducing the original DFT or training requires those external components and access to the relevant software and data. The recorded configuration is descriptive, not an executable fairchem training file.
