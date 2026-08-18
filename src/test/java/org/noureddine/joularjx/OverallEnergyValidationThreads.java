package org.noureddine.joularjx;

import java.util.ArrayList;
import java.util.List;

public class OverallEnergyValidationThreads {

    static class WorkerRunnable implements Runnable {
        private final int targetNumber;
        private final long runTimeMs;
        private long checksum = 0;

        public WorkerRunnable(int targetNumber, long runTimeMs) {
            this.targetNumber = targetNumber;
            this.runTimeMs = runTimeMs;
        }

        @Override
        public void run() {
            long endTime = System.currentTimeMillis() + runTimeMs;
            while (System.currentTimeMillis() < endTime) {
                checksum += PrimeUtils.sumOfPrimes(targetNumber);
            }
        }

        public long getChecksum() { return checksum; }
    }

    public static void testScenarioStandard() {
        System.out.println("[Threads Validation] Scenario A: 2 Concurrent Worker Threads (10s)...");
        Thread t1 = new Thread(new WorkerRunnable(5000, 10000), "Worker-1");
        Thread t2 = new Thread(new WorkerRunnable(5000, 10000), "Worker-2");
        t1.start();
        t2.start();
        try {
            t1.join();
            t2.join();
        } catch (InterruptedException ignored) {}
        System.out.println("[Threads Validation] Scenario A finished.");
    }

    public static void testScenarioSingleThread() {
        System.out.println("[Threads Validation] Scenario B1: Single Worker Thread Baseline...");
        Thread t1 = new Thread(new WorkerRunnable(4000, 5000), "SingleWorker");
        t1.start();
        try { t1.join(); } catch (InterruptedException ignored) {}
        System.out.println("[Threads Validation] Scenario B1 finished.");
    }

    public static void testScenarioThreadThrashing() {
        System.out.println("[Threads Validation] Scenario B2: 100 Short-lived Micro-threads...");
        List<Thread> threads = new ArrayList<>();
        for (int i = 0; i < 100; i++) {
            Thread t = new Thread(new WorkerRunnable(200, 5), "MicroThread-" + i);
            threads.add(t);
            t.start();
        }
        for (Thread t : threads) {
            try { t.join(); } catch (InterruptedException ignored) {}
        }
        System.out.println("[Threads Validation] Scenario B2 finished.");
    }

    public static void testScenarioAsymmetric() {
        System.out.println("[Threads Validation] Scenario B3: Asymmetric Idle vs Active Threads...");
        Thread busyThread = new Thread(new WorkerRunnable(5000, 5000), "BusyThread");
        Thread idleThread = new Thread(() -> {
            try { Thread.sleep(5000); } catch (InterruptedException ignored) {}
        }, "IdleThread");
        busyThread.start();
        idleThread.start();
        try {
            busyThread.join();
            idleThread.join();
        } catch (InterruptedException ignored) {}
        System.out.println("[Threads Validation] Scenario B3 finished.");
    }

    public static void testScenarioThreadCrash() {
        System.out.println("[Threads Validation] Scenario B4: Thread Runtime Crash...");
        Thread crashingThread = new Thread(() -> {
            long endTime = System.currentTimeMillis() + 1000;
            while (System.currentTimeMillis() < endTime) {
                PrimeUtils.sumOfPrimes(1000);
            }
            throw new RuntimeException("Simulated thread exception crash");
        }, "CrashingThread");
        crashingThread.start();
        try { crashingThread.join(); } catch (InterruptedException ignored) {}
        System.out.println("[Threads Validation] Scenario B4 finished.");
    }

    public static void testScenarioScale(int numThreads) {
        System.out.println("[Threads Validation] Scenario C: Scaling " + numThreads + " Concurrent Worker Threads...");
        List<Thread> threads = new ArrayList<>();
        for (int i = 0; i < numThreads; i++) {
            Thread t = new Thread(new WorkerRunnable(4000, 10000), "Worker-" + (i + 1));
            threads.add(t);
            t.start();
        }
        for (Thread t : threads) {
            try { t.join(); } catch (InterruptedException ignored) {}
        }
        System.out.println("[Threads Validation] Scenario C finished.");
    }

    public static void main(String[] args) {
        if (args.length > 0) {
            String mode = args[0];
            switch (mode) {
                case "B1": testScenarioSingleThread(); break;
                case "B2": testScenarioThreadThrashing(); break;
                case "B3": testScenarioAsymmetric(); break;
                case "B4": testScenarioThreadCrash(); break;
                case "C1": testScenarioScale(2); break;
                case "C2": testScenarioScale(4); break;
                case "C3": testScenarioScale(6); break;
                case "C4": testScenarioScale(8); break;
                default: testScenarioStandard(); break;
            }
        } else {
            testScenarioStandard();
        }
    }
}
