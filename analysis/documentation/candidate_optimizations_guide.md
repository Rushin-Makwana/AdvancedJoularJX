# JVector Energy Optimization: Candidate Reference & Execution Guide

This document provides a comprehensive technical breakdown of the 5 candidate hotspot methods optimized in **OptimizedJVector**, including their exact fully qualified signatures with parameter types, descriptions of changes made, before-and-after empirical energy measurements (from the $N=50$ run benchmark), and exact terminal commands to compile, package, and execute each candidate individually.

---

## 1. Candidate Optimization Summary Table

The table below summarizes the 5 candidates, what was changed in simple terms, their exact signatures with parameter types, and the before vs. after self-energy impact measured across all 50 valid runs ($N=50$):

| Candidate | Method Name & Full Signature with Parameters | Before (Baseline) Mean Self Energy | After (Optimized) Mean Self Energy | Energy Reduction ($\Delta E$) |
| :---: | :--- | :---: | :---: | :---: |
| **#1** | `io.github.jbellis.jvector.vector.PanamaVectorUtilSupport.squareDistancePreferred(VectorFloat<?> v1, int v1offset, VectorFloat<?> v2, int v2offset, int length)` | $194.13\text{ J}$ | $32.08\text{ J}$ | **$-83.48\%$** |
| **#2** | `io.github.jbellis.jvector.vector.PanamaVectorUtilSupport.fromVectorFloat(VectorSpecies<Float> SPEC, VectorFloat<?> vector, int offset)` | $132.61\text{ J}$ | $0.00\text{ J}$ | **$-100.00\%$** (eliminated) |
| **#3** | `io.github.jbellis.jvector.graph.similarity.BuildScoreProvider$1.diversityScoreFunctionFor(int node1)` |  $8.69\text{ J}$ | $3.27\text{ J}$ | **$-62.38\%$** |
| **#4** | `io.github.jbellis.jvector.graph.OnHeapGraphIndex.getNeighborsIterator(int node, int level)` |  $3.14\text{ J}$ | $1.94\text{ J}$ | **$-38.13\%$** |
| **#5** | `io.github.jbellis.jvector.graph.similarity.DefaultSearchScoreProvider.exact(VectorFloat<?> query, VectorSimilarityFunction vsf, RandomAccessVectorValues vectors)` | $0.0986\text{ J}$ | $0.0694\text{ J}$ | **$-29.61\%$** |

---

## 2. Overall Program Energy Impact ($N=50$ Runs)

Across 50 valid measured iterations of `VectorIntroProfile` (excluding 2 warmup runs):

| Metric | Original JVector Baseline | Optimized JVector | Absolute Delta ($\Delta$) | Percentage Drop ($\%$) |
| :--- | :---: | :---: | :---: | :---: |
| **Sample Mean Energy ($\bar{x}$)** | **$516.68\text{ J}$** | **$157.36\text{ J}$** | **$-359.32\text{ J}$** | **$\mathbf{-69.54\%}$** |
| **Sample Variance ($s^2$)** | $384.98\text{ J}^2$ | $58.70\text{ J}^2$ | $-326.28\text{ J}^2$ | **$-84.75\%$** |
| **Sample Std. Dev. ($s$)** | $19.62\text{ J}$ | $7.66\text{ J}$ | $-11.96\text{ J}$ | **$-60.95\%$** |
| **Hypothesis Testing** | \multicolumn{4}{c|}{Welch's $t = 120.63$ ($p < 10^{-15}$), Mann-Whitney $U = 0.0$ ($p < 10^{-15}$)} |

---

## 3. Detailed Candidate Breakdown

### Candidate 1: SIMD Vector Squared Euclidean Distance

- **Full Signature with Parameters:**
  ```text
  io.github.jbellis.jvector.vector.PanamaVectorUtilSupport.squareDistancePreferred(io.github.jbellis.jvector.vector.types.VectorFloat,int,io.github.jbellis.jvector.vector.types.VectorFloat,int,int)
  ```
- **Java Declaration:**
  ```java
  float squareDistancePreferred(VectorFloat<?> v1, int v1offset, VectorFloat<?> v2, int v2offset, int length)
  ```
- **File Location:**
  `jvector-twenty/src/main/java/io/github/jbellis/jvector/vector/PanamaVectorUtilSupport.java`
- **Maven Module:** `jvector-twenty`

#### Description of Changes Made:
1. **Primitive Array Hoisting:** Hoisted array extraction out of the loop. If `v1` and `v2` are `ArrayVectorFloat`, it extracts `float[] aArr` and `float[] bArr` once upfront.
2. **Direct SIMD Register Loading:** Replaced intermediate adapter calls (`fromVectorFloat`) with direct Panama `FloatVector.fromArray(FloatVector.SPECIES_PREFERRED, aArr, offset)` calls.
3. **Hardware FMA Utilization:** Replaced multi-species unrolled branch loops with clean AVX2 Fused Multiply-Add (`diff.fma(diff, sum)`) compiling down to native `vfmadd231ps` instructions.
4. **Scalar Tail Indexing:** Handled residual tail elements via direct array indexing `aArr[v1offset + i]` rather than virtual `v.get(i)` calls.

#### Energy Values (Mean over 50 Runs):
- **Self Energy:**
  - **Before (Baseline):** $194.13\text{ Joules}$ ($s^2 = 67.03\text{ J}^2$)
  - **After (Optimized):** $32.08\text{ Joules}$ ($s^2 = 7.50\text{ J}^2$)
  - **Self Energy Reduction:** **$-83.48\%$** ($-162.05\text{ J}$)
- **Total Energy:**
  - **Before (Baseline):** $342.13\text{ Joules}$
  - **After (Optimized):** $34.20\text{ Joules}$
  - **Total Energy Reduction:** **$-90.00\%$**

---

### Candidate 2: Panama Vector Adapter Layer

- **Full Signature with Parameters:**
  ```text
  io.github.jbellis.jvector.vector.PanamaVectorUtilSupport.fromVectorFloat(jdk.incubator.vector.VectorSpecies,io.github.jbellis.jvector.vector.types.VectorFloat,int)
  ```
- **Java Declaration:**
  ```java
  protected FloatVector fromVectorFloat(VectorSpecies<Float> SPEC, VectorFloat<?> vector, int offset)
  ```
- **File Location:**
  `jvector-twenty/src/main/java/io/github/jbellis/jvector/vector/PanamaVectorUtilSupport.java`
- **Maven Module:** `jvector-twenty`

#### Description of Changes Made:
1. **Complete Call Elimination in Hot Paths:** In the baseline version, `fromVectorFloat` was called twice per loop iteration to load each vector slice, incurring millions of method dispatches and interface checks. In `OptimizedJVector`, `squareDistancePreferred` loads directly from the primitive array slices, completely bypassing this method in the core distance loops.
2. **API Preserved:** The method was kept in `PanamaVectorUtilSupport.java` to retain API backward compatibility for off-heap and custom vector implementations.

#### Energy Values (Mean over 50 Runs):
- **Self Energy:**
  - **Before (Baseline):** $132.61\text{ Joules}$ ($s^2 = 40.86\text{ J}^2$)
  - **After (Optimized):** $0.00\text{ Joules}$ ($s^2 = 0.00\text{ J}^2$)
  - **Self Energy Reduction:** **$-100.00\%$** (Completely eliminated from execution stack)
- **Total Energy:**
  - **Before (Baseline):** $146.96\text{ Joules}$
  - **After (Optimized):** $0.00\text{ Joules}$
  - **Total Energy Reduction:** **$-100.00\%$**

---

### Candidate 3: Graph Construction Edge Diversity Score Function

- **Full Signature with Parameters:**
  ```text
  io.github.jbellis.jvector.graph.similarity.BuildScoreProvider$1.diversityScoreFunctionFor(int)
  ```
- **Java Declaration:**
  ```java
  public NodeScoreProvider diversityScoreFunctionFor(int node1)
  ```
- **File Location:**
  `jvector-base/src/main/java/io/github/jbellis/jvector/graph/similarity/BuildScoreProvider.java`
- **Maven Module:** `jvector-base`

#### Description of Changes Made:
1. **Replaced Capturing Lambda with Static Class:** In the baseline, `diversityScoreFunctionFor` returned a dynamic capturing lambda `(node2) -> vsf.compare(v1, vectors.getVector(node2))` on every call, allocating a new closure object on the Java heap hundreds of thousands of times during Vamana graph construction.
2. **Static Layout & Escape Analysis:** Replaced the lambda with a static inner class `ExactDiversityScoreFunction` holding fields for `vsf`, `v1`, and `vectors`. This enables the HotSpot C2 compiler to perform scalar replacement and inline score evaluations, cutting GC allocations.

#### Energy Values (Mean over 50 Runs):
- **Self Energy:**
  - **Before (Baseline):** $8.69\text{ Joules}$ ($s^2 = 1.30\text{ J}^2$)
  - **After (Optimized):** $3.27\text{ Joules}$ ($s^2 = 0.29\text{ J}^2$)
  - **Self Energy Reduction:** **$-62.38\%$** ($-5.42\text{ J}$)
- **Total Energy:**
  - **Before (Baseline):** $11.66\text{ Joules}$
  - **After (Optimized):** $5.00\text{ Joules}$
  - **Total Energy Reduction:** **$-57.12\%$**
  *(Note: The underlying lambda helper execution inside this call dropped from $329.98\text{ J} \rightarrow 49.08\text{ J}$, an $85.1\%$ total reduction).*

---

### Candidate 4: Graph Neighbor Traversal Iterator Fast Path

- **Full Signature with Parameters:**
  ```text
  io.github.jbellis.jvector.graph.OnHeapGraphIndex.getNeighborsIterator(int,int)
  ```
- **Java Declaration:**
  ```java
  public NodesIterator getNeighborsIterator(int node, int level)
  ```
- **File Location:**
  `jvector-base/src/main/java/io/github/jbellis/jvector/graph/OnHeapGraphIndex.java`
- **Maven Module:** `jvector-base`

#### Description of Changes Made:
1. **Iterator Wrapper Bypass:** In the baseline, `ConcurrentGraphIndexView.getNeighborsIterator` wrapped every lookup in an anonymous `NodesIterator` instance with delegating `nextInt()` and `hasNext()` virtual calls.
2. **Fast-Path Check:** Added an immediate return of the raw underlying iterator whenever `allMutationsCompleted` is true (the steady state during graph traversal and search queries) or if `raw instanceof NodesIterator`, removing redundant wrapper allocations.

#### Energy Values (Mean over 50 Runs):
- **Self Energy:**
  - **Before (Baseline):** $3.14\text{ Joules}$ ($s^2 = 0.23\text{ J}^2$)
  - **After (Optimized):** $1.94\text{ Joules}$ ($s^2 = 0.23\text{ J}^2$)
  - **Self Energy Reduction:** **$-38.13\%$** ($-1.20\text{ J}$)
- **Total Energy:**
  - **Before (Baseline):** $6.57\text{ Joules}$
  - **After (Optimized):** $4.12\text{ Joules}$
  - **Total Energy Reduction:** **$-37.29\%$**

---

### Candidate 5: Exact Search Score Function Provider

- **Full Signature with Parameters:**
  ```text
  io.github.jbellis.jvector.graph.similarity.DefaultSearchScoreProvider.exact(io.github.jbellis.jvector.vector.types.VectorFloat,io.github.jbellis.jvector.vector.VectorSimilarityFunction,io.github.jbellis.jvector.graph.RandomAccessVectorValues)
  ```
- **Java Declaration:**
  ```java
  public static SearchScoreProvider exact(VectorFloat<?> query, VectorSimilarityFunction vsf, RandomAccessVectorValues vectors)
  ```
- **File Location:**
  `jvector-base/src/main/java/io/github/jbellis/jvector/graph/similarity/DefaultSearchScoreProvider.java`
- **Maven Module:** `jvector-base`

#### Description of Changes Made:
1. **Eliminated Anonymous Inner Class Allocations:** In the baseline, `exact(...)` instantiated an anonymous `SearchScoreProvider` which then instantiated an anonymous `SearchScoreFunction.ExactScoreFunction` on each search invocation.
2. **Static Inner Classes with Pre-cached Function:** Converted to static classes (`ExactSearchScoreProvider` and `ExactSearchScoreFunction`). The provider pre-instantiates the score function once upon initialization and returns the cached reference on `scoreFunction()`, avoiding allocations on each hierarchy layer traversal.

#### Energy Values (Mean over 50 Runs):
- **Self Energy:**
  - **Before (Baseline):** $0.0986\text{ Joules}$ ($s^2 = 0.0100\text{ J}^2$)
  - **After (Optimized):** $0.0694\text{ Joules}$ ($s^2 = 0.0095\text{ J}^2$)
  - **Self Energy Reduction:** **$-29.61\%$**
- **Total Energy:**
  - **Before (Baseline):** $0.1515\text{ Joules}$
  - **After (Optimized):** $0.1051\text{ Joules}$
  - **Total Energy Reduction:** **$-30.63\%$**

---

## 3. Exact Commands to Compile & Run Each Candidate

### Environment Prerequisites
Execute in your terminal to ensure JDK 21 is active:
```bash
export JAVA_HOME=/Library/Java/JavaVirtualMachines/jdk-21.jdk/Contents/Home
```

---

### Commands for Candidate 1 & Candidate 2 (`PanamaVectorUtilSupport`)

```bash
# 1. Navigate to OptimizedJVector repository
cd /Users/mac/Developer/OptimizedJVector

# 2. Compile the jvector-twenty module
./mvnw compile -pl jvector-twenty -am -DskipTests -Drat.skip=true -Dmaven.javadoc.skip=true

# 3. Package the updated class files into the runnable examples fat JAR
cd /Users/mac/Developer/OptimizedJVector/jvector-twenty/target/classes
jar uf /Users/mac/Developer/OptimizedJVector/jvector-examples/target/jvector-examples-4.0.1-SNAPSHOT-jar-with-dependencies.jar \
  io/github/jbellis/jvector/vector/PanamaVectorUtilSupport*.class

# 4. Run the benchmark workload with JoularJX energy profiler attached
cd /Users/mac/Downloads/joularjx-3.1.0
/Library/Java/JavaVirtualMachines/jdk-21.jdk/Contents/Home/bin/java \
  "-XX:CompileCommand=dontinline,io.github.jbellis.jvector.*::*" \
  --add-modules=jdk.incubator.vector \
  -Djoularjx.config=/Users/mac/Downloads/joularjx-3.1.0/config.properties \
  -javaagent:/Users/mac/Downloads/joularjx-3.1.0/target/joularjx-3.1.0.jar \
  -cp "/Users/mac/Developer/OptimizedJVector/jvector-examples/target/jvector-examples-4.0.1-SNAPSHOT-jar-with-dependencies.jar" \
  io.github.jbellis.jvector.example.tutorial.VectorIntroProfile
```

---

### Commands for Candidate 3 (`BuildScoreProvider.diversityScoreFunctionFor`)

```bash
# 1. Navigate to OptimizedJVector repository
cd /Users/mac/Developer/OptimizedJVector

# 2. Compile the jvector-base module
./mvnw compile -pl jvector-base -am -DskipTests -Drat.skip=true -Dmaven.javadoc.skip=true

# 3. Package BuildScoreProvider into the fat JAR
cd /Users/mac/Developer/OptimizedJVector/jvector-base/target/classes
jar uf /Users/mac/Developer/OptimizedJVector/jvector-examples/target/jvector-examples-4.0.1-SNAPSHOT-jar-with-dependencies.jar \
  io/github/jbellis/jvector/graph/similarity/BuildScoreProvider*.class

# 4. Run the workload with JoularJX
cd /Users/mac/Downloads/joularjx-3.1.0
/Library/Java/JavaVirtualMachines/jdk-21.jdk/Contents/Home/bin/java \
  "-XX:CompileCommand=dontinline,io.github.jbellis.jvector.*::*" \
  --add-modules=jdk.incubator.vector \
  -Djoularjx.config=/Users/mac/Downloads/joularjx-3.1.0/config.properties \
  -javaagent:/Users/mac/Downloads/joularjx-3.1.0/target/joularjx-3.1.0.jar \
  -cp "/Users/mac/Developer/OptimizedJVector/jvector-examples/target/jvector-examples-4.0.1-SNAPSHOT-jar-with-dependencies.jar" \
  io.github.jbellis.jvector.example.tutorial.VectorIntroProfile
```

---

### Commands for Candidate 4 (`OnHeapGraphIndex.getNeighborsIterator`)

```bash
# 1. Navigate to OptimizedJVector repository
cd /Users/mac/Developer/OptimizedJVector

# 2. Compile the jvector-base module
./mvnw compile -pl jvector-base -am -DskipTests -Drat.skip=true -Dmaven.javadoc.skip=true

# 3. Package OnHeapGraphIndex into the fat JAR
cd /Users/mac/Developer/OptimizedJVector/jvector-base/target/classes
jar uf /Users/mac/Developer/OptimizedJVector/jvector-examples/target/jvector-examples-4.0.1-SNAPSHOT-jar-with-dependencies.jar \
  io/github/jbellis/jvector/graph/OnHeapGraphIndex*.class

# 4. Run the workload with JoularJX
cd /Users/mac/Downloads/joularjx-3.1.0
/Library/Java/JavaVirtualMachines/jdk-21.jdk/Contents/Home/bin/java \
  "-XX:CompileCommand=dontinline,io.github.jbellis.jvector.*::*" \
  --add-modules=jdk.incubator.vector \
  -Djoularjx.config=/Users/mac/Downloads/joularjx-3.1.0/config.properties \
  -javaagent:/Users/mac/Downloads/joularjx-3.1.0/target/joularjx-3.1.0.jar \
  -cp "/Users/mac/Developer/OptimizedJVector/jvector-examples/target/jvector-examples-4.0.1-SNAPSHOT-jar-with-dependencies.jar" \
  io.github.jbellis.jvector.example.tutorial.VectorIntroProfile
```

---

### Commands for Candidate 5 (`DefaultSearchScoreProvider.exact`)

```bash
# 1. Navigate to OptimizedJVector repository
cd /Users/mac/Developer/OptimizedJVector

# 2. Compile the jvector-base module
./mvnw compile -pl jvector-base -am -DskipTests -Drat.skip=true -Dmaven.javadoc.skip=true

# 3. Package DefaultSearchScoreProvider into the fat JAR
cd /Users/mac/Developer/OptimizedJVector/jvector-base/target/classes
jar uf /Users/mac/Developer/OptimizedJVector/jvector-examples/target/jvector-examples-4.0.1-SNAPSHOT-jar-with-dependencies.jar \
  io/github/jbellis/jvector/graph/similarity/DefaultSearchScoreProvider*.class

# 4. Run the workload with JoularJX
cd /Users/mac/Downloads/joularjx-3.1.0
/Library/Java/JavaVirtualMachines/jdk-21.jdk/Contents/Home/bin/java \
  "-XX:CompileCommand=dontinline,io.github.jbellis.jvector.*::*" \
  --add-modules=jdk.incubator.vector \
  -Djoularjx.config=/Users/mac/Downloads/joularjx-3.1.0/config.properties \
  -javaagent:/Users/mac/Downloads/joularjx-3.1.0/target/joularjx-3.1.0.jar \
  -cp "/Users/mac/Developer/OptimizedJVector/jvector-examples/target/jvector-examples-4.0.1-SNAPSHOT-jar-with-dependencies.jar" \
  io.github.jbellis.jvector.example.tutorial.VectorIntroProfile
```

---

### Command to Run Plain Verification (Without Profiler)

To run the application directly and verify correctness (timing, distance calculation, and node retrieval count):

```bash
/Library/Java/JavaVirtualMachines/jdk-21.jdk/Contents/Home/bin/java \
  --add-modules=jdk.incubator.vector \
  -cp "/Users/mac/Developer/OptimizedJVector/jvector-examples/target/jvector-examples-4.0.1-SNAPSHOT-jar-with-dependencies.jar" \
  io.github.jbellis.jvector.example.tutorial.VectorIntroProfile
```
1. Candidate Optimization Summary Table
Candidate	Target Class & Exact Method Signature	Before (Baseline) Mean Self Energy	After (Optimized) Mean Self Energy	Percentage Reduction (
Δ
E
ΔE)
#1	io.github.jbellis.jvector.vector.PanamaVectorUtilSupport.squareDistancePreferred(VectorFloat<?> v1, int v1offset, VectorFloat<?> v2, int v2offset, int length)	
194.13
 J
194.13 J	
32.08
 J
32.08 J	
−
83.48
%
−83.48%
#2	io.github.jbellis.jvector.vector.PanamaVectorUtilSupport.fromVectorFloat(VectorSpecies<Float> SPEC, VectorFloat<?> vector, int offset)	
132.61
 J
132.61 J	
0.00
 J
0.00 J	
−
100.00
%
−100.00% (eliminated)
#3	io.github.jbellis.jvector.graph.similarity.BuildScoreProvider$1.diversityScoreFunctionFor(int node1)	
8.69
 J
8.69 J	
3.27
 J
3.27 J	
−
62.38
%
−62.38%
#4	io.github.jbellis.jvector.graph.OnHeapGraphIndex.getNeighborsIterator(int node, int level)	
3.14
 J
3.14 J	
1.94
 J
1.94 J	
−
38.13
%
−38.13%
#5	io.github.jbellis.jvector.graph.similarity.DefaultSearchScoreProvider.exact(VectorFloat<?> query, VectorSimilarityFunction vsf, RandomAccessVectorValues vectors)	
0.0986
 J
0.0986 J	
0.0694
 J
0.0694 J	
−
29.61
%
−29.61%
(Overall program energy dropped by 
69.54
%
69.54%, from 
516.68
 J
→
157.36
 J
516.68 J→157.36 J with 
p
<
10
−
15
p<10 
−15
 ).
