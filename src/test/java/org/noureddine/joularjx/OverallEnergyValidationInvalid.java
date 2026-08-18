package org.noureddine.joularjx;

public class OverallEnergyValidationInvalid {
    public static void main(String[] args) {
        System.out.println("Starting invalid edge validation workload...");
        try {
            PrimeUtils.sumOfPrimes(-50);
            throw new AssertionError("Invalid edge case did not throw exception!");
        } catch (IllegalArgumentException e) {
            System.out.println("Invalid edge validation workload completed successfully (handled gracefully): " + e.getMessage());
        }
    }
}
