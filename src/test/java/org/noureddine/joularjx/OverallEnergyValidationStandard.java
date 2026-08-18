package org.noureddine.joularjx;

public class OverallEnergyValidationStandard {
    public static void main(String[] args) {
        System.out.println("Starting standard validation workload...");
        long start = System.currentTimeMillis();
        long result = 0;
        while (System.currentTimeMillis() - start < 10000) {
            result = PrimeUtils.sumOfPrimes(5000);
        }
        long expected = 1548136;
        if (result != expected) {
            throw new AssertionError("Checksum mismatch! Got: " + result + ", Expected: " + expected);
        }
        System.out.println("Standard validation workload completed successfully. Result: " + result);
    }
}
