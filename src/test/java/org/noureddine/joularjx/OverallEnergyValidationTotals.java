package org.noureddine.joularjx;

public class OverallEnergyValidationTotals {

    private static long processChild(int n) {
        long dummy = 0;
        for (int i = 0; i < 50; i++) {
            dummy += PrimeUtils.sumOfPrimes(n);
        }
        return dummy;
    }

    private static long processParent(int n) {
        long dummy = 0;
        for (int i = 0; i < 100; i++) {
            dummy += processChild(n);
        }
        return dummy;
    }

    private static long recursiveFactorial(int n) {
        if (n <= 1) return 1;
        long dummy = PrimeUtils.sumOfPrimes(100);
        return dummy + recursiveFactorial(n - 1);
    }

    public static void testScenarioStandard() {
        System.out.println("[Totals Validation] Scenario A: Standard Nested Hierarchy & Recursion (Depth 10)...");
        long endTime = System.currentTimeMillis() + 10000;
        long dummy = 0;
        while (System.currentTimeMillis() < endTime) {
            dummy += processParent(5000);
            dummy += recursiveFactorial(10);
        }
        System.out.println("[Totals Validation] Scenario A finished. Checksum: " + dummy);
    }

    public static void testScenarioLeafOnly() {
        System.out.println("[Totals Validation] Scenario B1: Direct Leaf-Only Call...");
        long endTime = System.currentTimeMillis() + 5000;
        long dummy = 0;
        while (System.currentTimeMillis() < endTime) {
            dummy += processChild(2000);
        }
        System.out.println("[Totals Validation] Scenario B1 finished. Checksum: " + dummy);
    }

    public static void testScenarioExceptionChild() {
        System.out.println("[Totals Validation] Scenario B2: Child Exception Abort...");
        long endTime = System.currentTimeMillis() + 2000;
        long dummy = 0;
        while (System.currentTimeMillis() < endTime) {
            dummy += processChild(1000);
        }
        throw new RuntimeException("Simulated exception inside child call hierarchy");
    }

    public static void testScenarioNullChild() {
        System.out.println("[Totals Validation] Scenario B3: Null-return Boundary...");
        long endTime = System.currentTimeMillis() + 5000;
        long dummy = 0;
        while (System.currentTimeMillis() < endTime) {
            Object obj = getNullObject();
            dummy += (obj == null) ? 1 : 0;
            dummy += processChild(1500);
        }
        System.out.println("[Totals Validation] Scenario B3 finished. Checksum: " + dummy);
    }

    private static Object getNullObject() {
        return null;
    }

    public static void testScenarioDeepRecursion() {
        System.out.println("[Totals Validation] Scenario B4: Deep Stack Recursion (Depth 1000)...");
        long endTime = System.currentTimeMillis() + 10000;
        long dummy = 0;
        while (System.currentTimeMillis() < endTime) {
            dummy += recursiveFactorial(1000);
        }
        System.out.println("[Totals Validation] Scenario B4 finished. Checksum: " + dummy);
    }

    public static void testScenarioScale(int depth, int iterations) {
        System.out.println("[Totals Validation] Scenario C: Depth " + depth + ", Iterations " + iterations + "...");
        long endTime = System.currentTimeMillis() + 10000;
        long dummy = 0;
        while (System.currentTimeMillis() < endTime) {
            for (int k = 0; k < iterations; k++) {
                dummy += processParent(2000);
            }
            dummy += recursiveFactorial(depth);
        }
        System.out.println("[Totals Validation] Scenario C finished. Checksum: " + dummy);
    }

    public static void main(String[] args) {
        if (args.length > 0) {
            String mode = args[0];
            switch (mode) {
                case "B1": testScenarioLeafOnly(); break;
                case "B2": testScenarioExceptionChild(); break;
                case "B3": testScenarioNullChild(); break;
                case "B4": testScenarioDeepRecursion(); break;
                case "C1": testScenarioScale(25, 500); break;
                case "C2": testScenarioScale(50, 1000); break;
                case "C3": testScenarioScale(75, 1500); break;
                case "C4": testScenarioScale(100, 2000); break;
                default: testScenarioStandard(); break;
            }
        } else {
            testScenarioStandard();
        }
    }
}
