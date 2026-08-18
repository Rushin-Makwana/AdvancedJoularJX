package org.noureddine.joularjx;

/**
 * Pure Java suite runner that executes the main methods of all overall energy
 * validation classes directly in sequence. 
 * Eliminates any testing framework abstractions and intermediate test helper methods.
 */
public class OverallEnergyTestSuite {

    public static void main(String[] args) {
        System.out.println("Starting OverallEnergyTestSuite...");
        
        try {
            System.out.println("--- Scenario A (Standard) ---");
            OverallEnergyValidationStandard.main(new String[0]);
        } catch (Exception e) {
            System.err.println("Standard Scenario failed: " + e.getMessage());
        }
        
        try {
            System.out.println("--- Scenario B(i) (Small) ---");
            OverallEnergyValidationSmall.main(new String[0]);
        } catch (Exception e) {
            System.err.println("Small Scenario failed: " + e.getMessage());
        }
        
        try {
            System.out.println("--- Scenario B(ii) (Large) ---");
            OverallEnergyValidationLarge.main(new String[0]);
        } catch (Exception e) {
            System.err.println("Large Scenario failed: " + e.getMessage());
        }
        
        try {
            System.out.println("--- Scenario B(iii) (Invalid) ---");
            OverallEnergyValidationInvalid.main(new String[0]);
        } catch (Exception e) {
            System.err.println("Invalid Scenario failed: " + e.getMessage());
        }
        
        try {
            System.out.println("--- Scenario C1 (Structured 1000) ---");
            OverallEnergyValidationStructured1000.main(new String[0]);
        } catch (Exception e) {
            System.err.println("Structured 1000 failed: " + e.getMessage());
        }
        
        try {
            System.out.println("--- Scenario C2 (Structured 2000) ---");
            OverallEnergyValidationStructured2000.main(new String[0]);
        } catch (Exception e) {
            System.err.println("Structured 2000 failed: " + e.getMessage());
        }
        
        System.out.println("OverallEnergyTestSuite completed.");
    }
}
