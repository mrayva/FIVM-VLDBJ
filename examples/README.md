# Examples Guide

This directory contains runnable example queries, toy datasets, generated code, and application wrappers for F-IVM.

## Layout

- `queries/`: hand-written F-IVM input SQL files grouped by workload (`simple`, `housing`, `retailer`, `tpch`, `favorita`, ...)
- `datasets/`: input data files used by the example SQL files
- `include/ring/`: custom aggregate/ring definitions referenced from SQL files
- `include/application/`: C++ application wrappers used when building runnable binaries
- `src/application/`: additional generated or hand-written application code for some workloads
- `generated/m3/`: generated M3 output from `make m3`
- `generated/cpp/`: generated C++ headers from `make cpp`
- `bin/`: compiled example executables
- `aux/`: helper scripts for generating variable orders and SQL assets
- `tods26-experiments/`: paper workflow assets and scripts

## Typical Flow

From the repository root:

```bash
scripts/generate-code.sh -l cpp examples/queries/simple/rst_RT.sql -o /tmp/rst_RT.hpp
scripts/build-generated-cpp.sh /tmp/rst_RT.hpp /tmp/rst_RT_app
```

Then run from `examples/` so relative dataset paths like `./datasets/simple/R.tbl` resolve correctly:

```bash
cd examples
/tmp/rst_RT_app --no-output
```

To compile many examples at once:

```bash
cd examples
make
build-examples.sh
```

## Anatomy Of An Example SQL File

Example: [`queries/simple/rst_RT.sql`](/home/mrayva/FIVM-VLDBJ/examples/queries/simple/rst_RT.sql)

An example file usually contains:

1. A variable order import:

```sql
IMPORT DTREE FROM FILE 'rst.txt';
```

2. Optional ring/type definitions:

```sql
CREATE TYPE RingCofactor
FROM FILE 'ring/ring_cofactor_degree1.hpp'
WITH PARAMETER SCHEMA (...);
```

3. Input sources:

```sql
CREATE STREAM R(A int, B float) FROM FILE './datasets/simple/R.tbl' LINE DELIMITED CSV;
CREATE TABLE S(A int, C int, E float, extra int) FROM FILE './datasets/simple/S.tbl' LINE DELIMITED CSV;
```

4. A restricted SQL aggregate query:

```sql
SELECT SUM(A*B*C*D) FROM R NATURAL JOIN S NATURAL JOIN T;
```

Notes:

- `CREATE STREAM` means the source is treated as dynamic input and processed via stream triggers.
- `CREATE TABLE` means the source is preloaded once and used during `ON SYSTEM READY`.
- Paths in `FROM FILE ...` are interpreted relative to the process working directory at runtime, not relative to the SQL file.
- `LINE DELIMITED CSV` means one row per line. The runtime CSV reader uses `,` by default unless `delimiter := '|'` or another delimiter is provided.

## Preparing Input Data

The runtime expects row-oriented text files whose field order matches the schema declared in the SQL file exactly.

For example:

```sql
CREATE STREAM R(A int, B float) FROM FILE './datasets/simple/R.tbl' LINE DELIMITED CSV;
```

expects `R.tbl` rows like:

```text
1,2
1,3
2,5
```

Rules:

- The number and order of columns must match the declared schema.
- Numeric and string types are parsed according to the declared SQL types.
- An optional extra trailing field is treated as the tuple payload/weight. If omitted, payload defaults to `1`.
- For files using the default CSV reader, extra trailing fields after the optional payload are rejected.
- Relative dataset paths should be chosen so the binary can be launched from the intended working directory, usually `examples/`.

The checked-in simple dataset is under [`datasets/simple`](/home/mrayva/FIVM-VLDBJ/examples/datasets/simple). The checked-in housing dataset is under [`datasets/housing-4-normalised`](/home/mrayva/FIVM-VLDBJ/examples/datasets/housing-4-normalised).

## Variable Order / DTree `.txt` Files

Example: [`queries/simple/rst.txt`](/home/mrayva/FIVM-VLDBJ/examples/queries/simple/rst.txt)

These files describe the variable order (tree decomposition) used by the compiler. The actual format is implemented in [`compiler/src/main/scala/fdbresearch/parsing/VariableOrderParser.scala`](/home/mrayva/FIVM-VLDBJ/compiler/src/main/scala/fdbresearch/parsing/VariableOrderParser.scala).

### High-Level Structure

The file has:

1. A header line with two integers
2. One line per variable
3. One line per relation

For `rst.txt`:

```text
5 3
0 A int -1 {} 0
1 B float 0 {0} 0
2 C int 0 {0} 0
3 D float 2 {2} 0
4 E float 2 {0,2} 0
5 extra int 4 {0,2,4} 0
R 1 A,B
T 3 C,D
S 5 A,C,E,extra
```

### Variable Lines

Grammar:

```text
<id> <name> <type> <parentId> {<keyIds>} <cacheFlag>
```

Example:

```text
0 A int -1 {} 0
```

Meaning:

- variable id: `0`
- name: `A`
- type: `int`
- parent id: `-1` means this is the root variable
- key ids: `{}` means no key dependencies listed here
- cache flag: parsed but not documented elsewhere in this repository

Another example:

```text
3 D float 2 {2} 0
```

means variable `D` is a child of variable node `2` (`C`).

### Relation Lines

Grammar:

```text
<relationName> <parentId> <var1,var2,...>
```

Example:

```text
R 1 A,B
```

Meaning:

- relation name: `R`
- attach this relation under variable node `1`
- relation keys/attributes used by the variable order: `A,B`

The parser turns these lines into `VariableOrderRelation` nodes attached under the referenced parent variable.

## How To Create A New Example

1. Add a SQL file under `examples/queries/<group>/`.
2. Add or reference a variable-order `.txt` file in the same directory.
3. Add any ring definition header under `examples/include/ring/` if needed.
4. Add dataset files under `examples/datasets/<group>/`.
5. Generate code with `scripts/generate-code.sh`.
6. If you want a runnable binary, compile it with `scripts/build-generated-cpp.sh` and provide an application wrapper if the default runtime behavior is not enough.

## Current Limitations

- There is no separate formal specification for the DTree `.txt` format beyond the parser implementation.
- Dataset preparation is described by convention in the SQL files and runtime parser behavior, not by a dedicated schema tool.
- Some experiment subdirectories contain workflow scripts rather than user-facing documentation.
