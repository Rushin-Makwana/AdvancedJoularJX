package org.noureddine.joularjx;

public class OverallEnergyValidationOverloads {

    public static long process(int n) {
        long dummy = 0;
        for (int i = 0; i < 20; i++) {
            dummy += PrimeUtils.sumOfPrimes(n);
        }
        return dummy;
    }

    public static long process(double d) {
        long dummy = 0;
        int n = (int) d;
        for (int i = 0; i < 20; i++) {
            dummy += PrimeUtils.sumOfPrimes(n);
        }
        return dummy;
    }

    public static long process(String str) {
        return str == null ? 1 : str.length();
    }

    public static long process(Object obj) {
        return obj == null ? 2 : obj.hashCode();
    }

    public static long process(byte b) {
        return b * 3L;
    }

    public static long process(short s) {
        return s * 7L;
    }

    public static long process(int... values) {
        long sum = 0;
        for (int v : values) sum += v;
        return sum;
    }

    public static void testScenarioStandard() {
        System.out.println("[Overloads Validation] Scenario A: Standard process(int) & process(double)...");
        long endTime = System.currentTimeMillis() + 10000;
        long dummy = 0;
        while (System.currentTimeMillis() < endTime) {
            dummy += process(5000);
            dummy += process(5000.0);
        }
        System.out.println("[Overloads Validation] Scenario A finished. Checksum: " + dummy);
    }

    public static void testScenarioNullObject() {
        System.out.println("[Overloads Validation] Scenario B1: Null Object Overloads...");
        long endTime = System.currentTimeMillis() + 5000;
        long dummy = 0;
        while (System.currentTimeMillis() < endTime) {
            String s = null;
            Object o = null;
            dummy += process(s);
            dummy += process(o);
            dummy += process(2000);
        }
        System.out.println("[Overloads Validation] Scenario B1 finished. Checksum: " + dummy);
    }

    public static void testScenarioPrimitiveCasting() {
        System.out.println("[Overloads Validation] Scenario B2: Primitive Byte/Short Overloads...");
        long endTime = System.currentTimeMillis() + 5000;
        long dummy = 0;
        byte b = 10;
        short s = 20;
        while (System.currentTimeMillis() < endTime) {
            dummy += process(b);
            dummy += process(s);
            dummy += process(3000);
        }
        System.out.println("[Overloads Validation] Scenario B2 finished. Checksum: " + dummy);
    }

    public static void testScenarioVarargs() {
        System.out.println("[Overloads Validation] Scenario B3: Varargs Overloads...");
        long endTime = System.currentTimeMillis() + 5000;
        long dummy = 0;
        while (System.currentTimeMillis() < endTime) {
            dummy += process(1, 2, 3, 4, 5);
            dummy += process(1000);
        }
        System.out.println("[Overloads Validation] Scenario B3 finished. Checksum: " + dummy);
    }

    public static void testScenarioSingleSignature() {
        System.out.println("[Overloads Validation] Scenario B4: Single Signature Non-Overloaded...");
        long endTime = System.currentTimeMillis() + 5000;
        long dummy = 0;
        while (System.currentTimeMillis() < endTime) {
            dummy += process(5000);
        }
        System.out.println("[Overloads Validation] Scenario B4 finished. Checksum: " + dummy);
    }

    public static void testScenarioScale(int iterations) {
        System.out.println("[Overloads Validation] Scenario C: Iterations " + iterations + "...");
        long endTime = System.currentTimeMillis() + 10000;
        long dummy = 0;
        while (System.currentTimeMillis() < endTime) {
            for (int k = 0; k < iterations; k++) {
                dummy += process(3000);
                dummy += process(3000.0);
            }
        }
        System.out.println("[Overloads Validation] Scenario C finished. Checksum: " + dummy);
    }

    public static void main(String[] args) {
        if (args.length > 0) {
            String mode = args[0];
            switch (mode) {
                case "B1": testScenarioNullObject(); break;
                case "B2": testScenarioPrimitiveCasting(); break;
                case "B3": testScenarioVarargs(); break;
                case "B4": testScenarioSingleSignature(); break;
                case "C1": testScenarioScale(500); break;
                case "C2": testScenarioScale(1000); break;
                case "C3": testScenarioScale(1500); break;
                case "C4": testScenarioScale(2000); break;
                default: testScenarioStandard(); break;
            }
        } else {
            testScenarioStandard();
        }
    }
}
