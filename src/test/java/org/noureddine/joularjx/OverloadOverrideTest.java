package org.noureddine.joularjx;

/**
 * Workload test to verify that JoularJX resolves overloaded method names
 * as well as overridden method calls in subclass polymorphism correctly.
 */
public class OverloadOverrideTest {

    /**
     * Interface representing a generic task executor.
     */
    interface Worker {
        /**
         * Executes a workload.
         *
         * @param input the input parameter
         * @return the result of execution
         */
        double execute(int input);
    }

    /**
     * Implementation of Worker performing sine operations.
     */
    static class SubWorkerA implements Worker {
        @Override
        public double execute(int input) {
            double acc = 0;
            for (int i = 0; i < 2000; i++) {
                acc += Math.sin(input + i);
            }
            return acc;
        }
    }

    /**
     * Implementation of Worker performing cosine operations.
     */
    static class SubWorkerB implements Worker {
        @Override
        public double execute(int input) {
            double acc = 0;
            for (int i = 0; i < 2000; i++) {
                acc += Math.cos(input + i);
            }
            return acc;
        }
    }

    /**
     * Main entry point to run the OverloadOverrideTest workload.
     * Runs for a duration of 10 seconds.
     *
     * @param args the command-line arguments
     * @throws InterruptedException if the execution is interrupted
     */
    public static void main(String[] args) throws InterruptedException {
        System.out.println("Starting OverloadOverrideTest workload...");
        long start = System.currentTimeMillis();
        double sum = 0;
        Worker workerA = new SubWorkerA();
        Worker workerB = new SubWorkerB();

        // Run loop for 10 seconds calling overloaded and overridden methods
        while (System.currentTimeMillis() - start < 10000) {
            sum += compute(42);
            sum += compute(4.2);
            sum += workerA.execute(5);
            sum += workerB.execute(10);
        }
        System.out.println("OverloadOverrideTest finished. Sum: " + sum);
    }

    /**
     * Overloaded compute method with int signature.
     *
     * @param val the integer value
     * @return the computed sum
     */
    public static double compute(int val) {
        double acc = 0;
        for (int i = 0; i < 2000; i++) {
            acc += Math.sin(val + i);
        }
        return acc;
    }

    /**
     * Overloaded compute method with double signature.
     *
     * @param val the double value
     * @return the computed sum
     */
    public static double compute(double val) {
        double acc = 0;
        for (int i = 0; i < 2000; i++) {
            acc += Math.cos(val + i);
        }
        return acc;
    }
}
