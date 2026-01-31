# TPC-H Q10 - All Variable Orders Cost Computation

> **Note:** All values computed by `q10_all_vo_cost.py`.
> Run `python3 q10_all_vo_cost.py --batch 10000` to regenerate.

## View Tree Structures

### vo1: orderkey → custkey → nationkey
```
V_NCOL (root, @orderkey, AGG)
├── L^P
└── V_NCO (@custkey)
    ├── O^P
    └── V_NC (@nationkey)
        ├── N
        └── C
```

### vo2: orderkey → nationkey → custkey
```
V_NCOL (root, @orderkey, AGG)
├── L^P
└── V_NCO (@nationkey)
    ├── N
    └── V_CO (@custkey)
        ├── C
        └── O^P
```

### vo3: nationkey → custkey → orderkey
```
V_NCOL (root, @nationkey)
├── N
└── V_COL (@custkey)
    ├── C
    └── V_OL (@orderkey, AGG → custkey)
        ├── O^P
        └── L^P
```

### vo4: nationkey → orderkey → custkey
```
V_NCOL (root, @nationkey)
├── N
└── V_COL (@orderkey, AGG → custkey)
    ├── L^P
    └── V_CO (@custkey)
        ├── C
        └── O^P
```

### vo5: bushy (custkey root)
```
V_NCOL (root, @custkey)
├── V_NC (@nationkey)
│   ├── N
│   └── C
└── V_OL (@orderkey, AGG → custkey)
    ├── O^P
    └── L^P
```

---

## Statistics (TPC-H SF=1, 10k batch)

### Batch Sizes

| Relation | With Predicates | No Predicates |
|----------|-----------------|---------------|
| U_N | 0 (or 1) | 0 (or 1) |
| U_C | 196 | 196 |
| U_O | 75 | 1,961 |
| U_L | 1,933 | 7,844 |

### Key Join Degrees

| Degree | With Predicates | No Predicates |
|--------|-----------------|---------------|
| deg_L(*\|okey) | 2.01 | 4.00 |
| deg_O(*\|okey) | 0.076 | 1.0 |
| deg_C(*\|nkey) | 6,000 | 6,000 |
| deg_V_OL(*\|ckey) | 0.253 | 0.667 |
| deg_V_COL(*\|nkey) | 1,519 | 6,000 |

### Domain Sizes

| Domain | With Predicates | No Predicates |
|--------|-----------------|---------------|
| \|Dom(custkey)\| | 37,967 | 99,996 |
| \|Dom(orderkey)\| | 49,028 | 1,500,000 |

---

## Cost Comparison

### Static Scenario (U_N = 0)

| VO | With Predicates | No Predicates | Ratio |
|----|-----------------|---------------|-------|
| vo1 | 1,238 | 51,178 | 41x |
| vo2 | 1,192 | 54,903 | 46x |
| vo3 | 1,880 | 94,383 | 50x |
| vo4 | 1,936 | 98,042 | 51x |
| vo5 | 1,433 | 63,074 | 44x |

**Rankings (lower is better):**
- With predicates: vo2 < vo1 < vo5 < vo3 < vo4
- No predicates: vo1 < vo2 < vo5 < vo3 < vo4

### Dynamic Scenario (U_N = 1)

| VO | With Predicates | No Predicates | Ratio |
|----|-----------------|---------------|-------|
| vo1 | 18,698 | 597,275 | 32x |
| vo2 | 12,651 | 595,000 | 47x |
| vo3 | 3,398 | 100,383 | 30x |
| vo4 | 3,454 | 104,042 | 30x |
| vo5 | 8,951 | 73,074 | 8x |

**Rankings (lower is better):**
- With predicates: vo3 < vo4 < vo5 < vo2 < vo1
- No predicates: vo5 < vo3 < vo4 < vo2 < vo1

---

## Detailed Breakdown (With Predicates, Static)

| VO | S_N | S_C | S_O | S_L | Total |
|----|-----|-----|-----|-----|-------|
| vo1 | 0 | 570 | 374 | 294 | 1,238 |
| vo2 | 0 | 449 | 449 | 294 | 1,192 |
| vo3 | 0 | 99 | 900 | 881 | 1,880 |
| vo4 | 0 | 674 | 674 | 587 | 1,936 |
| vo5 | 0 | 246 | 600 | 587 | 1,433 |

---

## Key Observations

### 1. Optimal VO Depends on Nation Update Pattern

- **Static nation (U_N=0):** vo1 and vo2 are best
  - Aggregation at root minimizes path costs for O/L updates
  - Nation's position doesn't matter when it's not updated

- **Dynamic nation (U_N=1):** vo3 and vo4 are best
  - Nation is at the root (1 hop)
  - vo1/vo2 have nation at depth 2-3, causing massive S_N

### 2. Nation Update Cost by VO

| VO | S_N (with pred) | S_N (no pred) | Nation Depth |
|----|-----------------|---------------|--------------|
| vo1 | 17,460 | 546,097 | 3 |
| vo2 | 11,459 | 540,097 | 2 |
| vo3 | 1,519 | 6,000 | 1 |
| vo4 | 1,519 | 6,000 | 1 |
| vo5 | 7,518 | 10,000 | 2 |

### 3. vo5 (Bushy) Provides Balance

- Competitive in both static and dynamic scenarios
- Nation at depth 2, but path doesn't traverse aggregation node
- Best choice when nation update frequency is uncertain

### 4. Predicate Impact

- Predicates reduce costs by ~40-50x across all VOs
- Affects both batch sizes and join degrees
