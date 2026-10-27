"""Merge individual coffea outputs WITHOUT calling postprocess() a second time.

The issue: when using `dask@lxplus` with `--process-separately`, each per-dataset
.coffea file already has postprocess() applied (divides by sum_genweights).
Running `pocket-coffea merge-outputs` calls postprocess() again, double-dividing.

This script just accumulates the files without postprocessing.

Usage (inside container with myenv):
    python merge_no_postprocess.py fit_templates_HHbbgg_2024_glopart/output_all.coffea fit_templates_HHbbgg_2024_glopart/*.coffea
    # First arg is output path, rest are input files
"""
import sys
import os
import glob
from coffea.util import load, save
from coffea.processor import accumulate


def main():
    if len(sys.argv) < 3:
        print("Usage: python merge_no_postprocess.py <output.coffea> <input1.coffea> [input2.coffea ...]")
        sys.exit(1)

    outfile = sys.argv[1]
    infiles = sys.argv[2:]

    # Exclude the output file and any previous merged files from inputs (in case of glob overlap)
    infiles = [f for f in infiles if os.path.abspath(f) != os.path.abspath(outfile)]
    infiles = [f for f in infiles if not os.path.basename(f).startswith('output_all')]

    print(f"Merging {len(infiles)} files into {outfile}")
    print(f"  (WITHOUT calling postprocess - files already have sum_genweights division)")

    outputs = []
    for f in sorted(infiles):
        print(f"  Loading {os.path.basename(f)}...")
        outputs.append(load(f))

    print("Accumulating...")
    merged = accumulate(outputs)

    print(f"Saving to {outfile}...")
    save(merged, outfile)
    print("Done.")


if __name__ == '__main__':
    main()