"""
experiments_catalog.py
Preconfigured dictionary of all experiments and graphs generated with JoularJX.
Can be imported into run_experiments.py and analyze_experiments.py, or used as a standalone reference.
"""

# Common paths
JAVA_BIN = "/Library/Java/JavaVirtualMachines/jdk-21.jdk/Contents/Home/bin/java"
EXTENDED_AGENT_JAR = "/Users/mac/Downloads/joularjx-3.1.0/target/joularjx-3.1.0.jar"
ORIGINAL_AGENT_JAR = "/Users/mac/Documents/RA/joularjx/target/joularjx-3.0.0.jar"

JVECTOR_BASELINE_JAR = "/Users/mac/Developer/jvector/jvector-examples/target/jvector-examples-4.0.1-SNAPSHOT-jar-with-dependencies.jar"
JVECTOR_OPTIMIZED_JAR = "/Users/mac/Developer/OptimizedJVector/jvector-examples/target/jvector-examples-4.0.1-SNAPSHOT-jar-with-dependencies.jar"

MICROBENCH_CLASSPATH = "target/test-classes:target/classes"

EXPERIMENTS = {
    # =========================================================================
    # PART 1: Real-World JVector 5 Optimization Candidates (VectorIntroProfile)
    # =========================================================================
    "jvector_candidate1_squareDistancePreferred": {
        "title": "JVector Candidate 1: SIMD Vector Squared Distance",
        "target_class": "io.github.jbellis.jvector.example.tutorial.VectorIntroProfile",
        "target_metric": "io.github.jbellis.jvector.vector.PanamaVectorUtilSupport.squareDistancePreferred(io.github.jbellis.jvector.vector.types.VectorFloat,int,io.github.jbellis.jvector.vector.types.VectorFloat,int,int)",
        "method_energy_column": "Self Energy (Joules)",
        "workload_jar_baseline": JVECTOR_BASELINE_JAR,
        "workload_jar_optimized": JVECTOR_OPTIMIZED_JAR,
        "histogram": "candidate1_squareDistancePreferred_self_energy_comparison.png",
        "raw_data_dir_baseline": "analysis/raw_data/joularjx/VectorIntroProfile",
        "raw_data_dir_optimized": "analysis/raw_data/joularjx-3.1.0/VectorIntroProfile",
    },
    "jvector_candidate2_fromVectorFloat": {
        "title": "JVector Candidate 2: Panama Vector Float Adapter Layer",
        "target_class": "io.github.jbellis.jvector.example.tutorial.VectorIntroProfile",
        "target_metric": "io.github.jbellis.jvector.vector.PanamaVectorUtilSupport.fromVectorFloat(jdk.incubator.vector.VectorSpecies,io.github.jbellis.jvector.vector.types.VectorFloat,int)",
        "method_energy_column": "Self Energy (Joules)",
        "workload_jar_baseline": JVECTOR_BASELINE_JAR,
        "workload_jar_optimized": JVECTOR_OPTIMIZED_JAR,
        "histogram": "candidate2_fromVectorFloat_self_energy_comparison.png",
        "raw_data_dir_baseline": "analysis/raw_data/joularjx/VectorIntroProfile",
        "raw_data_dir_optimized": "analysis/raw_data/joularjx-3.1.0/VectorIntroProfile",
    },
    "jvector_candidate3_diversityScoreFunctionFor": {
        "title": "JVector Candidate 3: Graph Construction Edge Diversity Score",
        "target_class": "io.github.jbellis.jvector.example.tutorial.VectorIntroProfile",
        "target_metric": "io.github.jbellis.jvector.graph.similarity.BuildScoreProvider$1.diversityScoreFunctionFor(int)",
        "method_energy_column": "Self Energy (Joules)",
        "workload_jar_baseline": JVECTOR_BASELINE_JAR,
        "workload_jar_optimized": JVECTOR_OPTIMIZED_JAR,
        "histogram": "candidate3_diversityScoreFunctionFor_self_energy_comparison.png",
        "raw_data_dir_baseline": "analysis/raw_data/joularjx/VectorIntroProfile",
        "raw_data_dir_optimized": "analysis/raw_data/joularjx-3.1.0/VectorIntroProfile",
    },
    "jvector_candidate4_getNeighborsIterator": {
        "title": "JVector Candidate 4: Graph Neighbor Traversal Iterator Fast Path",
        "target_class": "io.github.jbellis.jvector.example.tutorial.VectorIntroProfile",
        "target_metric": "io.github.jbellis.jvector.graph.OnHeapGraphIndex.getNeighborsIterator(int,int)",
        "method_energy_column": "Self Energy (Joules)",
        "workload_jar_baseline": JVECTOR_BASELINE_JAR,
        "workload_jar_optimized": JVECTOR_OPTIMIZED_JAR,
        "histogram": "candidate4_getNeighborsIterator_self_energy_comparison.png",
        "raw_data_dir_baseline": "analysis/raw_data/joularjx/VectorIntroProfile",
        "raw_data_dir_optimized": "analysis/raw_data/joularjx-3.1.0/VectorIntroProfile",
    },
    "jvector_candidate5_exact": {
        "title": "JVector Candidate 5: Exact Search Score Function Provider",
        "target_class": "io.github.jbellis.jvector.example.tutorial.VectorIntroProfile",
        "target_metric": "io.github.jbellis.jvector.graph.similarity.DefaultSearchScoreProvider.exact(io.github.jbellis.jvector.vector.types.VectorFloat,io.github.jbellis.jvector.vector.VectorSimilarityFunction,io.github.jbellis.jvector.graph.RandomAccessVectorValues)",
        "method_energy_column": "Self Energy (Joules)",
        "workload_jar_baseline": JVECTOR_BASELINE_JAR,
        "workload_jar_optimized": JVECTOR_OPTIMIZED_JAR,
        "histogram": "candidate5_exact_self_energy_comparison.png",
        "raw_data_dir_baseline": "analysis/raw_data/joularjx/VectorIntroProfile",
        "raw_data_dir_optimized": "analysis/raw_data/joularjx-3.1.0/VectorIntroProfile",
    },
    "jvector_profile_total_program": {
        "title": "JVector Profile Benchmark: Total Program Energy (50 Runs)",
        "target_class": "io.github.jbellis.jvector.example.tutorial.VectorIntroProfile",
        "target_metric": "TOTAL_PROGRAM",
        "method_energy_column": "Total Energy (Joules)",
        "workload_jar_baseline": JVECTOR_BASELINE_JAR,
        "workload_jar_optimized": JVECTOR_OPTIMIZED_JAR,
        "histogram": "jvector/TOTAL_PROGRAM_20260921_223307.png",
        "raw_data_dir_baseline": "analysis/raw_data/joularjx/VectorIntroProfile",
        "raw_data_dir_optimized": "analysis/raw_data/joularjx-3.1.0/VectorIntroProfile",
    },

    # =========================================================================
    # PART 2: Real-World JVector Tutorial Profiling (VectorIntro)
    # =========================================================================
    "jvector_intro_main": {
        "title": "JVector Intro: main Orchestrator",
        "target_class": "io.github.jbellis.jvector.example.tutorial.VectorIntro",
        "target_metric": "io.github.jbellis.jvector.example.tutorial.VectorIntro.main(java.lang.String[])",
        "method_energy_column": "Total Energy (Joules)",
        "workload_jar": JVECTOR_BASELINE_JAR,
        "histogram": "jvector/VectorIntro_main_20260910_004212.png",
        "raw_data_dir": "analysis/raw_data/joularjx-3.1.0/VectorIntro",
    },
    "jvector_intro_addGraphNode_VectorFloat": {
        "title": "JVector Intro: addGraphNode Overload (VectorFloat)",
        "target_class": "io.github.jbellis.jvector.example.tutorial.VectorIntro",
        "target_metric": "io.github.jbellis.jvector.graph.GraphIndexBuilder.addGraphNode(int,io.github.jbellis.jvector.vector.types.VectorFloat)",
        "method_energy_column": "Total Energy (Joules)",
        "workload_jar": JVECTOR_BASELINE_JAR,
        "histogram": "jvector/addGraphNode_VectorFloat_20260910_004212.png",
        "raw_data_dir": "analysis/raw_data/joularjx-3.1.0/VectorIntro",
    },
    "jvector_intro_addGraphNode_SearchScoreProvider": {
        "title": "JVector Intro: addGraphNode Overload (SearchScoreProvider)",
        "target_class": "io.github.jbellis.jvector.example.tutorial.VectorIntro",
        "target_metric": "io.github.jbellis.jvector.graph.GraphIndexBuilder.addGraphNode(int,io.github.jbellis.jvector.graph.similarity.SearchScoreProvider)",
        "method_energy_column": "Total Energy (Joules)",
        "workload_jar": JVECTOR_BASELINE_JAR,
        "histogram": "jvector/addGraphNode_SearchScoreProvider_20260910_004212.png",
        "raw_data_dir": "analysis/raw_data/joularjx-3.1.0/VectorIntro",
    },
    "jvector_intro_squareDistance64": {
        "title": "JVector Intro: SIMD squareDistance64 Kernel",
        "target_class": "io.github.jbellis.jvector.example.tutorial.VectorIntro",
        "target_metric": "io.github.jbellis.jvector.vector.PanamaVectorUtilSupport.squareDistance64(io.github.jbellis.jvector.vector.types.VectorFloat,int,io.github.jbellis.jvector.vector.types.VectorFloat,int,int)",
        "method_energy_column": "Total Energy (Joules)",
        "workload_jar": JVECTOR_BASELINE_JAR,
        "histogram": "jvector/Panama_squareDistance64_20260910_004212.png",
        "raw_data_dir": "analysis/raw_data/joularjx-3.1.0/VectorIntro",
    },
    "jvector_intro_CompletionTracker_init": {
        "title": "JVector Intro: CompletionTracker Constructor",
        "target_class": "io.github.jbellis.jvector.example.tutorial.VectorIntro",
        "target_metric": "io.github.jbellis.jvector.graph.OnHeapGraphIndex$CompletionTracker.<init>(int)",
        "method_energy_column": "Total Energy (Joules)",
        "workload_jar": JVECTOR_BASELINE_JAR,
        "histogram": "jvector/CompletionTracker_init_20260910_004212.png",
        "raw_data_dir": "analysis/raw_data/joularjx-3.1.0/VectorIntro",
    },
    "jvector_intro_total_program": {
        "title": "JVector Intro: Total Program Energy",
        "target_class": "io.github.jbellis.jvector.example.tutorial.VectorIntro",
        "target_metric": "TOTAL_PROGRAM",
        "method_energy_column": "Total Energy (Joules)",
        "workload_jar": JVECTOR_BASELINE_JAR,
        "histogram": "jvector/TOTAL_PROGRAM_20260929_020531.png",
        "raw_data_dir": "analysis/raw_data/joularjx-3.1.0/VectorIntro",
    },

    # =========================================================================
    # PART 3: JoularJX Core Feature Validation Suite
    # =========================================================================
    "validation_totals_isPrime": {
        "title": "Validation Totals: PrimeUtils.isPrime(int)",
        "target_class": "org.noureddine.joularjx.OverallEnergyValidationTotals",
        "target_metric": "org.noureddine.joularjx.PrimeUtils.isPrime(int)",
        "method_energy_column": "Total Energy (Joules)",
        "classpath": MICROBENCH_CLASSPATH,
        "histogram": "both_totalorg_noureddine_joularjx_PrimeUtils_isPrime_int__20260818_133107.png",
        "raw_data_dir": "analysis/raw_data/OverallEnergyValidationTotals",
    },
    "validation_totals_sumOfPrimes": {
        "title": "Validation Totals: PrimeUtils.sumOfPrimes(int)",
        "target_class": "org.noureddine.joularjx.OverallEnergyValidationTotals",
        "target_metric": "org.noureddine.joularjx.PrimeUtils.sumOfPrimes(int)",
        "method_energy_column": "Total Energy (Joules)",
        "classpath": MICROBENCH_CLASSPATH,
        "histogram": "org_noureddine_joularjx_PrimeUtils_sumOfPrimes_int__20260819_230314.png",
        "raw_data_dir": "analysis/raw_data/OverallEnergyValidationTotals",
    },
    "validation_overloads_isPrime": {
        "title": "Validation Overloads: PrimeUtils.isPrime(int)",
        "target_class": "org.noureddine.joularjx.OverallEnergyValidationOverloads",
        "target_metric": "org.noureddine.joularjx.PrimeUtils.isPrime(int)",
        "method_energy_column": "Total Energy (Joules)",
        "classpath": MICROBENCH_CLASSPATH,
        "histogram": "both_overloadorg_noureddine_joularjx_PrimeUtils_isPrime_int__20260818_123845.png",
        "raw_data_dir": "analysis/raw_data/OverallEnergyValidationOverloads",
    },
    "validation_overloads_process_int": {
        "title": "Validation Overloads: OverloadTest.process(int)",
        "target_class": "org.noureddine.joularjx.OverloadTest",
        "target_metric": "org.noureddine.joularjx.OverloadTest.process(int)",
        "method_energy_column": "Total Energy (Joules)",
        "classpath": MICROBENCH_CLASSPATH,
        "histogram": "4org.noureddine.joularjx.OverloadTest.process_20260803_210228.png",
        "raw_data_dir": "analysis/raw_data/OverloadTest",
    },
    "validation_overloads_process_double": {
        "title": "Validation Overloads: OverloadTest.process(double)",
        "target_class": "org.noureddine.joularjx.OverloadTest",
        "target_metric": "org.noureddine.joularjx.OverloadTest.process(double)",
        "method_energy_column": "Total Energy (Joules)",
        "classpath": MICROBENCH_CLASSPATH,
        "histogram": "4org.noureddine.joularjx.OverloadTest.process_20260803_210228.png",
        "raw_data_dir": "analysis/raw_data/OverloadTest",
    },
    "validation_sampling_total_program": {
        "title": "Validation Sampling: Total Program Energy",
        "target_class": "org.noureddine.joularjx.OverallEnergyValidationSampling",
        "target_metric": "TOTAL_PROGRAM",
        "method_energy_column": "Total Energy (Joules)",
        "classpath": MICROBENCH_CLASSPATH,
        "histogram": "TOTALlastsample_PROGRAM_20260818_184029.png",
        "raw_data_dir": "analysis/raw_data/OverallEnergyValidationSampling",
    },
    "validation_sampling_isPrime": {
        "title": "Validation Sampling: PrimeUtils.isPrime(int)",
        "target_class": "org.noureddine.joularjx.OverallEnergyValidationSampling",
        "target_metric": "org.noureddine.joularjx.PrimeUtils.isPrime(int)",
        "method_energy_column": "Total Energy (Joules)",
        "classpath": MICROBENCH_CLASSPATH,
        "histogram": "org_noureddine_joularjx_PrimeUtils_isPrime_int__20260820_172042.png",
        "raw_data_dir": "analysis/raw_data/OverallEnergyValidationSampling",
    },
    "validation_threads_total": {
        "title": "Validation Threads: Multi-threaded Total Program Energy",
        "target_class": "org.noureddine.joularjx.OverallEnergyValidationThreads",
        "target_metric": "TOTALthread_PROGRAM",
        "method_energy_column": "Total Energy (Joules)",
        "classpath": MICROBENCH_CLASSPATH,
        "histogram": "TOTALthread_PROGRAM_20260818_191823.png",
        "raw_data_dir": "analysis/raw_data/OverallEnergyValidationThreads",
    },
    "sampling_4way_comparison": {
        "title": "4-Way Sampling Window Study (1000/10 vs 10000/5000 vs 1000/500 vs Orig)",
        "target_class": "org.noureddine.joularjx.OverallEnergyValidationSampling",
        "target_metric": "TOTAL_PROGRAM",
        "method_energy_column": "Total Energy (Joules)",
        "classpath": MICROBENCH_CLASSPATH,
        "histogram": "sampling_4way_comparison_20260910_142743.png",
        "config_1_dir": "analysis/raw_data/joularjx-3.1.0_1000_10/OverallEnergyValidationSampling",
        "config_2_dir": "analysis/raw_data/joularjx-3.1.0_10000_5000/OverallEnergyValidationSampling",
        "config_3_dir": "analysis/raw_data/joularjx-3.1.0_1000_500/OverallEnergyValidationSampling",
        "config_orig_dir": "../raw_data/joularjx/OverallEnergyValidationSampling",
    },
}

if __name__ == "__main__":
    import sys
    print("=" * 80)
    print("JoularJX Experiments Catalog & Reference")
    print("=" * 80)
    print(f"Total Preconfigured Experiments: {len(EXPERIMENTS)}\n")
    for key, val in EXPERIMENTS.items():
        print(f"[{key}]")
        print(f"  Title:   {val['title']}")
        print(f"  Class:   {val['target_class']}")
        print(f"  Metric:  {val['target_metric']}")
        print(f"  Column:  {val.get('method_energy_column', 'N/A')}")
        if 'workload_jar_baseline' in val:
            print(f"  JAR:     {val['workload_jar_baseline']}")
        elif 'workload_jar' in val:
            print(f"  JAR:     {val['workload_jar']}")
        elif 'classpath' in val:
            print(f"  CP:      {val['classpath']}")
        print(f"  Graph:   {val.get('histogram', 'N/A')}\n")
