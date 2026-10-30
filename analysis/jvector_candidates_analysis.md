# Empirical Energy Profiling & Statistical Analysis of JVector Candidates

## 1. Executive Summary & Research Motivation

In software energy profiling with **JoularJX**, evaluating method-level energy efficiency requires distinguishing between **Total Energy** (inclusive of all callee subroutines on the JVM call stack) and **Self Energy** (energy dissipated strictly by the bytecode instructions executing directly within the method's own stack frame).

When investigating real-world vector database engines like **JVector** ([`jvector`](https://github.com/jbellis/jvector)), high-level orchestrators such as [`GraphIndexBuilder.addGraphNode`](file:///Users/mac/Developer/jvector/jvector-base/src/main/java/io/github/jbellis/jvector/graph/GraphIndexBuilder.java#L554-L605) show total energy propagating up the call hierarchy ($\approx 0.060\text{ J}$), but register near-zero Self Energy ($\approx 0.000\text{ J}$) because they delegate all computational arithmetic and synchronization downward.

To evaluate method-level energy profiles, we analyzed 40 valid experimental runs (plus 2 warm-up cycles) across all 3,101 monitored methods in the unmodified JVector tutorial workload ([`VectorIntro.java`](file:///Users/mac/Developer/jvector/jvector-examples/src/main/java/io/github/jbellis/jvector/example/tutorial/VectorIntro.java#L42-L117)) using native hardware `powermetrics` monitoring.

---

## 2. Statistical Summary Table ($N = 40$ Valid Runs, Native `powermetrics`)

The table below summarizes empirical metrics collected under native hardware energy monitoring across 40 valid runs:

| Candidate Method | Architectural Domain | Self Energy Mean ($\bar{x}$) | Self Energy Var ($s^2$) | Self Energy Range | Total Energy Mean ($\bar{x}$) | Total Energy Range | Histogram Link |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **[`VectorIntro.main`](file:///Users/mac/Developer/jvector/jvector-examples/src/main/java/io/github/jbellis/jvector/example/tutorial/VectorIntro.java#L43-L117)** | Workload Driver / Orchestrator | **`0.0217 J`** | `0.0045 J²` | `[0.0000, 0.2725] J` | **`18.1113 J`** | `[10.6357, 24.0923] J` | [Histogram](file:///Users/mac/Downloads/joularjx-3.1.0/analysis/histograms/jvector/VectorIntro_main_20260910_004212.png) |
| **[`GraphIndexBuilder.addGraphNode`](file:///Users/mac/Developer/jvector/jvector-base/src/main/java/io/github/jbellis/jvector/graph/GraphIndexBuilder.java#L554-L605)** (`VectorFloat`) | Graph Builder (`VectorFloat`) | **`0.0000 J`** | `0.0000 J²` | `[0.0000, 0.0000] J` | **`0.0604 J`** | `[0.0000, 0.1681] J` | [Histogram](file:///Users/mac/Downloads/joularjx-3.1.0/analysis/histograms/jvector/addGraphNode_VectorFloat_20260910_004212.png) |
| **[`GraphIndexBuilder.addGraphNode`](file:///Users/mac/Developer/jvector/jvector-base/src/main/java/io/github/jbellis/jvector/graph/GraphIndexBuilder.java#L554-L605)** (`SearchScoreProvider`) | Graph Builder (`SearchScoreProvider`) | **`0.0003 J`** | `0.0000 J²` | `[0.0000, 0.0104] J` | **`0.0599 J`** | `[0.0000, 0.1681] J` | [Histogram](file:///Users/mac/Downloads/joularjx-3.1.0/analysis/histograms/jvector/addGraphNode_SearchScoreProvider_20260910_004212.png) |
| **[`PanamaVectorUtilSupport.squareDistance64`](file:///Users/mac/Developer/jvector/jvector-twenty/src/main/java/io/github/jbellis/jvector/vector/PanamaVectorUtilSupport.java#L414-L425)** | Hardware SIMD Vector Kernel | **`0.0001 J`** | `0.0000 J²` | `[0.0000, 0.0046] J` | **`0.0293 J`** | `[0.0000, 0.2952] J` | [Histogram](file:///Users/mac/Downloads/joularjx-3.1.0/analysis/histograms/jvector/Panama_squareDistance64_20260910_004212.png) |
| **[`CompletionTracker.<init>`](file:///Users/mac/Developer/jvector/jvector-base/src/main/java/io/github/jbellis/jvector/graph/OnHeapGraphIndex.java#L639-L645)** | Concurrency / Memory Barriers | **`0.0000 J`** | `0.0000 J²` | `[0.0000, 0.0000] J` | **`0.0284 J`** | `[0.0000, 0.3011] J` | [Histogram](file:///Users/mac/Downloads/joularjx-3.1.0/analysis/histograms/jvector/CompletionTracker_init_20260910_004212.png) |

---

## 3. Four-Way Candidate Comparison

To visualize how energy dissipates across different layers of the JVector hierarchy simultaneously, the multi-panel comparison below compiles the 40-run empirical distributions of the primary candidates side by side:

![JVector 4-Way Candidates Comparison](file:///Users/mac/Downloads/joularjx-3.1.0/analysis/histograms/jvector/jvector_4way_candidates_comparison.png)

*Direct Link: [`jvector_4way_candidates_comparison.png`](file:///Users/mac/Downloads/joularjx-3.1.0/analysis/histograms/jvector/jvector_4way_candidates_comparison.png)*

### Comparison Insights:
1. **Macro vs. Micro Scale**: While top-level orchestration (`VectorIntro.main`) operates in the tens of Joules ($\approx 18.11\text{ J}$) by aggregating the entire workload, internal indexing and calculation routines operate in the hundredths/thousandths of a Joule ($0.02\text{--}0.06\text{ J}$).
2. **Deterministic Clustering**: Both overloaded variants of `addGraphNode` (panels b and c) track identical execution dynamics across graph insertion steps.
3. **SIMD Kernel Burst**: Vector similarity (`squareDistance64`, panel d) executes with extreme efficiency on Apple Silicon hardware vector lanes, exhibiting a tight unimodal distribution near zero with sparse bursts during active search phases.

---

## 4. In-Depth Candidate Analysis & Individual Histograms

---

### Candidate 1: `VectorIntro.main(String[])`
*Location: [`VectorIntro.java:43-117`](file:///Users/mac/Developer/jvector/jvector-examples/src/main/java/io/github/jbellis/jvector/example/tutorial/VectorIntro.java#L43-L117)*

#### Architectural Motivation & Distribution:
The top-level application entry point coordinates synthetic vector initialization, builder instantiation, graph construction, and search queries. 
- While its **Total Energy** encompasses the entire process runtime ($\bar{x} = 18.1113\text{ J}$, range $[10.6357\text{ J}, 24.0923\text{ J}]$), its **Self Energy** ($\bar{x} = 0.0217\text{ J}$) isolates the bytecode instructions executed directly within its own frame.
- **Why Total Energy is $\sim 18\text{--}21\text{ J}$**:
  As verified in [`VectorIntro_merged_average_energy.csv`](file:///Users/mac/Downloads/joularjx-3.1.0/analysis/merged_results/VectorIntro_merged_average_energy.csv), over $99.5\%$ of this energy is consumed by child subroutines:
  1. `BuiltinClassLoader.loadClass`: **`7.91 Joules`** loading 600+ classes.
  2. `GraphIndexBuilder.<clinit>`: **`15.06 Joules`** (static class initialization triggering Log4j2 and SLF4J logger bootstrap).
  3. `PanamaVectorizationProvider`: Detecting CPU SIMD architecture and initializing vector species bindings.

#### Histogram:
![VectorIntro.main Distribution](file:///Users/mac/Downloads/joularjx-3.1.0/analysis/histograms/jvector/VectorIntro_main_20260910_004212.png)

*Direct Link: [`VectorIntro_main_20260910_004212.png`](file:///Users/mac/Downloads/joularjx-3.1.0/analysis/histograms/jvector/VectorIntro_main_20260910_004212.png)*

---

### Candidate 2: `GraphIndexBuilder.addGraphNode(...)`
*Location: [`GraphIndexBuilder.java:554-605`](file:///Users/mac/Developer/jvector/jvector-base/src/main/java/io/github/jbellis/jvector/graph/GraphIndexBuilder.java#L554-L605)*

#### Architectural Motivation & Distribution:
`addGraphNode` serves as the primary insertion orchestrator in HNSW indexing. Extended JoularJX disambiguates the overloaded versions using dynamic BCEL parameter descriptor resolution:

#### Candidate 2a: `addGraphNode(int, VectorFloat)`
- **Total Energy**: **`0.0604 Joules`** ($s^2 = 0.001949\text{ J}^2$, active in 31 of 40 runs, max $0.1681\text{ J}$).
- **Self Energy**: **`0.0000 Joules`**.

![addGraphNode(VectorFloat) Distribution](file:///Users/mac/Downloads/joularjx-3.1.0/analysis/histograms/jvector/addGraphNode_VectorFloat_20260910_004212.png)

*Direct Link: [`addGraphNode_VectorFloat_20260910_004212.png`](file:///Users/mac/Downloads/joularjx-3.1.0/analysis/histograms/jvector/addGraphNode_VectorFloat_20260910_004212.png)*

#### Candidate 2b: `addGraphNode(int, SearchScoreProvider)`
- **Total Energy**: **`0.0599 Joules`** ($s^2 = 0.001929\text{ J}^2$, active in 31 of 40 runs, max $0.1681\text{ J}$).
- **Self Energy**: **`0.0003 Joules`**.

![addGraphNode(SearchScoreProvider) Distribution](file:///Users/mac/Downloads/joularjx-3.1.0/analysis/histograms/jvector/addGraphNode_SearchScoreProvider_20260910_004212.png)

*Direct Link: [`addGraphNode_SearchScoreProvider_20260910_004212.png`](file:///Users/mac/Downloads/joularjx-3.1.0/analysis/histograms/jvector/addGraphNode_SearchScoreProvider_20260910_004212.png)*

- **Why energy is $< 0.1\text{ J}$**:
  In `VectorIntro`, only **3 two-dimensional vectors** are inserted into the graph. The entire graph insertion completes in under $1\text{--}2\text{ milliseconds}$ of active CPU time ($\approx 15\text{ W} \times 0.002\text{ s} \approx 0.03\text{ J}$).
  When sub-sampled every $10\text{ ms}$, in 9 runs the insertion finished between sampling intervals ($0.0\text{ J}$), and in 31 runs it was captured during the sampling window ($\approx 0.05\text{--}0.168\text{ J}$).

---

### Candidate 3: `PanamaVectorUtilSupport.squareDistance64(...)`
*Location: [`PanamaVectorUtilSupport.java:414-425`](file:///Users/mac/Developer/jvector/jvector-twenty/src/main/java/io/github/jbellis/jvector/vector/PanamaVectorUtilSupport.java#L414-L425)*

#### Architectural Motivation:
This is the numerical compute kernel of JVector. When Panama vectorization is enabled via `--add-modules=jdk.incubator.vector`, JVector delegates distance calculations to unrolled AVX / NEON hardware vector lanes:
- In `VectorIntro`, query scoring executes a very small number of similarity comparisons.
- **Total Energy**: **`0.0293 Joules`** ($s^2 = 0.002234\text{ J}^2$, active in 29 runs, max $0.2952\text{ J}$).
- **Self Energy**: **`0.0001 Joules`**.

#### Histogram:
![Panama SIMD squareDistance64 Distribution](file:///Users/mac/Downloads/joularjx-3.1.0/analysis/histograms/jvector/Panama_squareDistance64_20260910_004212.png)

*Direct Link: [`Panama_squareDistance64_20260910_004212.png`](file:///Users/mac/Downloads/joularjx-3.1.0/analysis/histograms/jvector/Panama_squareDistance64_20260910_004212.png)*

---

### Candidate 4: `CompletionTracker.<init>`
*Location: [`OnHeapGraphIndex.java:639-645`](file:///Users/mac/Developer/jvector/jvector-base/src/main/java/io/github/jbellis/jvector/graph/OnHeapGraphIndex.java#L639-L645)*

#### Architectural Motivation:
Coordinates multi-threaded latch synchronization and memory barrier handoffs during concurrent graph updates:
- **Total Energy**: **`0.0284 Joules`** ($s^2 = 0.006024\text{ J}^2$, max $0.3011\text{ J}$).
- **Self Energy**: **`0.0000 Joules`**.

#### Histogram:
![CompletionTracker.<init> Distribution](file:///Users/mac/Downloads/joularjx-3.1.0/analysis/histograms/jvector/CompletionTracker_init_20260910_004212.png)

*Direct Link: [`CompletionTracker_init_20260910_004212.png`](file:///Users/mac/Downloads/joularjx-3.1.0/analysis/histograms/jvector/CompletionTracker_init_20260910_004212.png)*

---

## 5. Consolidated Data File & Histogram Locations

All raw data, aggregated results, and distribution plots are organized in the project directory:

- **Raw Data Directory (Native `powermetrics`)**: [`analysis/raw_data/joularjx-3.1.0/VectorIntro/`](file:///Users/mac/Downloads/joularjx-3.1.0/analysis/raw_data/joularjx-3.1.0/VectorIntro/)
  - Consolidated run totals: [`total_energies.csv`](file:///Users/mac/Downloads/joularjx-3.1.0/analysis/raw_data/joularjx-3.1.0/VectorIntro/total_energies.csv) (mean: $18.11\text{ J}$)
  - Run CSVs: `run_1.csv` through `run_42.csv`
- **Merged Averages**: [`analysis/merged_results/VectorIntro_merged_average_energy.csv`](file:///Users/mac/Downloads/joularjx-3.1.0/analysis/merged_results/VectorIntro_merged_average_energy.csv)
- **Dedicated JVector Histograms Directory**: [`analysis/histograms/jvector/`](file:///Users/mac/Downloads/joularjx-3.1.0/analysis/histograms/jvector/)
  - **4-Way Comparison Plot**: [`jvector_4way_candidates_comparison.png`](file:///Users/mac/Downloads/joularjx-3.1.0/analysis/histograms/jvector/jvector_4way_candidates_comparison.png)
  - `VectorIntro.main`: [`VectorIntro_main_20260910_004212.png`](file:///Users/mac/Downloads/joularjx-3.1.0/analysis/histograms/jvector/VectorIntro_main_20260910_004212.png)
  - `addGraphNode(int, VectorFloat)`: [`addGraphNode_VectorFloat_20260910_004212.png`](file:///Users/mac/Downloads/joularjx-3.1.0/analysis/histograms/jvector/addGraphNode_VectorFloat_20260910_004212.png)
  - `addGraphNode(int, SearchScoreProvider)`: [`addGraphNode_SearchScoreProvider_20260910_004212.png`](file:///Users/mac/Downloads/joularjx-3.1.0/analysis/histograms/jvector/addGraphNode_SearchScoreProvider_20260910_004212.png)
  - `squareDistance64`: [`Panama_squareDistance64_20260910_004212.png`](file:///Users/mac/Downloads/joularjx-3.1.0/analysis/histograms/jvector/Panama_squareDistance64_20260910_004212.png)
  - `CompletionTracker.<init>`: [`CompletionTracker_init_20260910_004212.png`](file:///Users/mac/Downloads/joularjx-3.1.0/analysis/histograms/jvector/CompletionTracker_init_20260910_004212.png)

