package org.noureddine.joularjx;

public class OverallEnergyValidationStructured2000 {
    public static void main(String[] args) {
        System.out.println("Starting structured validation workload (2000 iterations)...");
        long result = 0;
        for (int i = 0; i < 2000; i++) {
            result += PrimeUtils.sumOfPrimes(2000);
        }
        System.out.println("Structured validation workload (2000 iterations) completed. Result: " + result);
    }
}
