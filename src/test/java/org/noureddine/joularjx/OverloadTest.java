package org.noureddine.joularjx;

public class OverloadTest {
    public static void main(String[] args) throws InterruptedException {
        System.out.println("Starting OverloadTest workload...");
        long start = System.currentTimeMillis();
        double total = 0;
        // Run for about 10 seconds
        while (System.currentTimeMillis() - start < 10000) {
            total += process(42);
            total += process(4.2);
        }
        System.out.println("OverloadTest workload finished. Result: " + total);
    }

    public static double process(int x) {
        double acc = 0;
        for (int i = 0; i < 5000; i++) {
            acc += Math.sin(x + i);
        }
        return acc;
    }

    public static double process(double x) {
        double acc = 0;
        for (int i = 0; i < 5000; i++) {
            acc += Math.cos(x + i);
        }
        return acc;
    }
}
