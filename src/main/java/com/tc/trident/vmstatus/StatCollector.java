
package com.tc.trident.vmstatus;

import java.io.Closeable;
import java.io.IOException;
import java.lang.management.GarbageCollectorMXBean;
import java.lang.management.ManagementFactory;
import java.lang.management.MemoryMXBean;
import java.lang.management.ThreadMXBean;
import java.util.ArrayList;
import java.util.List;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import com.tc.trident.core.TridentException;
import com.tc.trident.store.StatStore;
import com.tc.trident.util.HostUtils;

/**
 * A daemon thread indented to collect JVM runtime information.
 *
 * @author kozz.gaof
 * @date Jan 14, 2015 11:24:47 AM
 * @id $Id$
 */
public class StatCollector extends Thread implements Closeable {
    
    private static final Logger logger = LoggerFactory.getLogger(StatCollector.class);
    
    private static final String HOSTNAME = HostUtils.getLocalHostName();
    
    private static final String HOSTIP = HostUtils.getHostIP();
    
    private StatStore statStore;
    
    private volatile boolean running = true;
    
    private long interval = 60 * 1000; // 60 seconds
    
    public void setStatStore(StatStore statStore) {
    
        this.statStore = statStore;
    }
    
    public void stopCollector() {
    
        running = false;
    }
    
    @Override
    public void run() {
    
        while (running) {
            long start = System.currentTimeMillis();
            if (logger.isDebugEnabled()) {
                logger.debug(">>>>>>>>>>> start collecting JVM runtime information...");
            }
            HeartBeat heartBeat = new HeartBeat(HOSTNAME, HOSTIP);
            heartBeat.setMemoryInfo(getMemoryInfo());
            heartBeat.setThreadsInfo(getThreadInfo());
            heartBeat.setGcInfoList(getGCInfoList());
            try {
                statStore.store(heartBeat);
            } catch (TridentException e) {
                logger.error("==========> Failed in store statistics info! " + heartBeat, e);
            }
            
            long elapsed = System.currentTimeMillis() - start;
            
            if (elapsed < interval) {
                try {
                    Thread.sleep(interval - elapsed);
                } catch (InterruptedException e) {
                    
                    logger.warn("==========> stop collecting because of InterruptedException");
                    break;
                }
            }
        }
        
    }
    
    public MemoryInfo getMemoryInfo() {
    
        MemoryMXBean memoryMXBean = ManagementFactory.getMemoryMXBean();
        MemoryInfo memoryInfo = new MemoryInfo();
        memoryInfo.setMaxHeap(memoryMXBean.getHeapMemoryUsage().getMax());
        memoryInfo.setUsedHeap(memoryMXBean.getHeapMemoryUsage().getUsed());
        memoryInfo.setMaxNonHeap(memoryMXBean.getNonHeapMemoryUsage().getMax());
        memoryInfo.setUsedNonHeap(memoryMXBean.getNonHeapMemoryUsage().getUsed());
        
        return memoryInfo;
    }
    
    public ThreadInfo getThreadInfo() {
    
        ThreadMXBean threadMXBean = ManagementFactory.getThreadMXBean();
        threadMXBean.setThreadContentionMonitoringEnabled(true);
        ThreadInfo threadInfo = new ThreadInfo();
        threadInfo.setActive(threadMXBean.getThreadCount());
        threadInfo.setDaemon(threadMXBean.getDaemonThreadCount());
        threadInfo.setPeek(threadMXBean.getPeakThreadCount());
        
        java.lang.management.ThreadInfo[] threads = threadMXBean.dumpAllThreads(true, true);
        int tomcatThreadsCount = countThreadsByPrefix(threads, "http-");
        int jettyThreadsCount = countThreadsBySubstring(threads, "qtp");
        
        threadInfo.setHttp(tomcatThreadsCount + jettyThreadsCount);
        return threadInfo;
    }
    
    private int countThreadsByPrefix(java.lang.management.ThreadInfo[] threads, String... prefixes) {
    
        int count = 0;
        
        for (java.lang.management.ThreadInfo thread : threads) {
            for (String prefix : prefixes) {
                if (thread.getThreadName().startsWith(prefix)) {
                    count++;
                }
            }
        }
        
        return count;
    }
    
    private int countThreadsBySubstring(java.lang.management.ThreadInfo[] threads, String... substrings) {
    
        int count = 0;
        
        for (java.lang.management.ThreadInfo thread : threads) {
            for (String str : substrings) {
                if (thread.getThreadName().contains(str)) {
                    count++;
                }
            }
        }
        
        return count;
    }
    
    public List<GCInfo> getGCInfoList() {
    
        List<GarbageCollectorMXBean> gcMXBeans = ManagementFactory.getGarbageCollectorMXBeans();
        ArrayList<GCInfo> gcInfoList = new ArrayList<GCInfo>();
        
        for (GarbageCollectorMXBean gcMXbean : gcMXBeans) {
            if (gcMXbean.isValid()) {
                GCInfo gc = new GCInfo();
                
                gc.setName(gcMXbean.getName());
                gc.setCount(gcMXbean.getCollectionCount());
                gc.setTime(gcMXbean.getCollectionTime());
                gcInfoList.add(gc);
            }
        }
        
        return gcInfoList;
    }
    
    @Override
    public void close() throws IOException {
    
        running = false;
        this.interrupt();
        statStore.close();
    }
}
