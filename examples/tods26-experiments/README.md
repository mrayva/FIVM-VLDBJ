# TODS26 TPCH Q10 Experiments

This directory organizes TPCH Q10 runs for a small matrix of scenarios:
- scale factors: `sf0p1`, `sf1`
- small tables mode: `static`, `dynamic`
- predicates: `with_pred` (original WHERE) or `no_pred` (removed predicates)

How to run (matrix, all VOs)
```
cd FIVM/examples/tods26-experiments
./run_q10_matrix.sh                     # default batch size 10000, all VOs
BATCH_SIZE=5000 ./run_q10_matrix.sh     # override batch size
TEST_MODE=1 ./run_q10_matrix.sh         # run only the first combo (sanity check)
```
Each run generates:
- C++: `generated/cpp/tods26/<vo>_<scale>_<mode>_pred_<on|off>.hpp`
- Binary: `bin/tods26/<vo>_<scale>_<mode>_pred_<on|off>`
- Log: `tods26-experiments/output/<vo>_<scale>_<mode>_pred_<on|off>.csv`

Regenerate assets (VOs + SQL)
```
cd FIVM/examples/tods26-experiments/queries/tpch_query_10
python generate_assets.py
```

Contents
- `queries/tpch_query_10/variable_orders/`: VO (strategy) files.
- `queries/tpch_query_10/sql_files/`: Q10 SQL variants (auto-generated).
- `queries/tpch_query_10/generate_assets.py`: regenerates all VOs + SQLs.
- `run_q10_matrix.sh`: build-and-run all combinations; writes logs.
- `output/`: CSV logs (rows,inserts,deletes,duration_ms).
- `plots/`: placeholder for figures.
- `plots/generate_throughput_plots.py`: creates throughput vs. percent-processed charts from logs.

Flags/behavior
- Uses `/usr/bin/time` to print wall time per run.
- Respects `FIVM_BATCH_LOG` internally (set automatically by scripts).
- `set -euo pipefail` in scripts:
  - `-e`: exit on any command error,
  - `-u`: treat unset vars as errors,
  - `-o pipefail`: a pipeline fails if any stage fails.

Notes
- Datasets live in `examples/datasets/updates_<scale>_b10000_{shared,static,dynamic}`.
- Application include: `include/application/tpch/application_tpch_query10.hpp` (shared across variants).
- To add plots, write scripts that consume the CSVs in `output/` and emit files into `plots/`.
- Throughput plotting: `cd plots && python generate_throughput_plots.py --input-dir ../output --output-dir .`
