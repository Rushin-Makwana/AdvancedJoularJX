package org.noureddine.joularjx;

public class OverallEnergyValidationSampling {

    public static void testScenarioStandard() {
        System.out.println("[Sampling Validation] Scenario A: Standard 10s execution...");
        long endTime = System.currentTimeMillis() + 10000;
        long dummy = 0;
        while (System.currentTimeMillis() < endTime) {
            dummy += PrimeUtils.sumOfPrimes(5000);
        }
        System.out.println("[Sampling Validation] Scenario A finished. Dummy checksum: " + dummy);
    }

    public static void testScenarioMicroRun() {
        System.out.println("[Sampling Validation] Scenario B1: Micro-runtime (<20ms)...");
        long dummy = 0;
        long endTime = System.currentTimeMillis() + 5;
        while (System.currentTimeMillis() < endTime) {
            dummy += PrimeUtils.sumOfPrimes(100);
        }
        System.out.println("[Sampling Validation] Scenario B1 finished. Checksum: " + dummy);
    }

    public static void testScenarioGCPause() {
        System.out.println("[Sampling Validation] Scenario B2: Injected GC Pause...");
        long endTime = System.currentTimeMillis() + 5000;
        long dummy = 0;
        while (System.currentTimeMillis() < endTime) {
            dummy += PrimeUtils.sumOfPrimes(2000);
        }
        System.out.println("[Sampling Validation] Triggering explicit System.gc()...");
        System.gc();
        try { Thread.sleep(300); } catch (InterruptedException ignored) {}
        endTime = System.currentTimeMillis() + 5000;
        while (System.currentTimeMillis() < endTime) {
            dummy += PrimeUtils.sumOfPrimes(2000);
        }
        System.out.println("[Sampling Validation] Scenario B2 finished. Checksum: " + dummy);
    }

    public static void testScenarioAbort() {
        System.out.println("[Sampling Validation] Scenario B3: Exception Abort mid-execution...");
        long endTime = System.currentTimeMillis() + 3000;
        long dummy = 0;
        while (System.currentTimeMillis() < endTime) {
            dummy += PrimeUtils.sumOfPrimes(1000);
        }
        throw new RuntimeException("Simulated runtime failure for sampling boundary test");
    }

    public static void testScenarioFractionalOffset() {
        System.out.println("[Sampling Validation] Scenario B4: Fractional Window Offset (10.4s)...");
        long endTime = System.currentTimeMillis() + 10400;
        long dummy = 0;
        while (System.currentTimeMillis() < endTime) {
            dummy += PrimeUtils.sumOfPrimes(3000);
        }
        System.out.println("[Sampling Validation] Scenario B4 finished. Checksum: " + dummy);
    }

    public static void testScenarioScale(int durationSeconds) {
        System.out.println("[Sampling Validation] Scenario C: Structured Duration " + durationSeconds + "s...");
        long endTime = System.currentTimeMillis() + (durationSeconds * 1000L);
        long dummy = 0;
        while (System.currentTimeMillis() < endTime) {
            dummy += PrimeUtils.sumOfPrimes(4000);
        }
        System.out.println("[Sampling Validation] Duration " + durationSeconds + "s finished. Checksum: " + dummy);
    }

    public static void main(String[] args) {
        if (args.length > 0) {
            String mode = args[0];
            switch (mode) {
                case "B1": testScenarioMicroRun(); break;
                case "B2": testScenarioGCPause(); break;
                case "B3": testScenarioAbort(); break;
                case "B4": testScenarioFractionalOffset(); break;
                case "C1": testScenarioScale(5); break;
                case "C2": testScenarioScale(10); break;
                case "C3": testScenarioScale(15); break;
                case "C4": testScenarioScale(20); break;
                default: testScenarioStandard(); break;
            }
        } else {
            testScenarioStandard();
        }
    }
}
