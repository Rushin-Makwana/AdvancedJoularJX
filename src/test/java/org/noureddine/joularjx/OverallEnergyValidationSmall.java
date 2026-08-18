package org.noureddine.joularjx;

public class OverallEnergyValidationSmall {
    public static void main(String[] args) {
        System.out.println("Starting small edge validation workload...");
        long result = PrimeUtils.sumOfPrimes(1);
        if (result != 0) {
            throw new AssertionError("Checksum mismatch! Got: " + result + ", Expected: 0");
        }
        System.out.println("Small edge validation workload completed successfully. Result: " + result);
    }
}
