package org.noureddine.joularjx;

public class OverallEnergyValidationLarge {
    public static void main(String[] args) {
        System.out.println("Starting large edge validation workload...");
        long start = System.currentTimeMillis();
        long result = 0;
        while (System.currentTimeMillis() - start < 15000) {
            result += PrimeUtils.sumOfPrimes(100000);
        }
        System.out.println("Large edge validation workload completed successfully. Result: " + result);
    }
}
