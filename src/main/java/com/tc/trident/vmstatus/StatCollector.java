
package com.tc.trident.vmstatus;

import java.io.Closeable;
import java.io.IOException;
import java.lang.reflect.Constructor;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import com.dianping.cat.message.internal.MilliSecondTimer;
import com.dianping.cat.message.spi.MessageStatistics;
import com.dianping.cat.message.spi.internal.DefaultMessageStatistics;
import com.dianping.cat.status.model.IVisitor;
import com.dianping.cat.status.model.entity.StatusInfo;
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
    
    private long interval = 10 * 1000; // 60 seconds
    
    public void setStatStore(StatStore statStore) {
    
        this.statStore = statStore;
    }
    
    public void stopCollector() {
    
        running = false;
    }
    
    @Override
    public void run() {
    
        while (running) {
            long start = MilliSecondTimer.currentTimeMillis();
            StatusInfo status = new StatusInfo();
            IVisitor visitor = (IVisitor) getStatusInfoCollectorInstance(new DefaultMessageStatistics());
            if (visitor != null) {
                if (logger.isDebugEnabled()) {
                    logger.debug(">>>>>>>>>>> start collecting JVM runtime information...");
                }
                status.accept(visitor);
                HeartBeat heartBeat = new HeartBeat(HOSTNAME, HOSTIP);
                heartBeat.setMemoryInfo(status.getMemory());
                heartBeat.setThreadsInfo(status.getThread());
                try {
                    statStore.store(heartBeat);
                } catch (TridentException e) {
                    logger.error("==========> Failed in store statistics info! " + heartBeat, e);
                }
            }
            
            long elapsed = MilliSecondTimer.currentTimeMillis() - start;
            
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
    
    private Class<?> statusInfoCollectorClass = null;
    private Constructor<?> cons = null;
    
    // since Frankie.Wu remove the <b>public</b> modifier from StatusInfoCollector.
    // some dirty hack must be put here.
    public Object getStatusInfoCollectorInstance(MessageStatistics messageStatistics) {
    
        try {
            if (statusInfoCollectorClass == null || cons == null) {
                statusInfoCollectorClass = Thread.currentThread().getContextClassLoader().loadClass("com.dianping.cat.status.StatusInfoCollector");
                cons = statusInfoCollectorClass.getConstructor(MessageStatistics.class);
                cons.setAccessible(true); // to neglect the default access modifier.
            }
            return cons.newInstance(messageStatistics);
        } catch (Exception e) {
            e.printStackTrace();
            return null;
        }
    }
    
    @Override
    public void close() throws IOException {
    
        running = false;
        this.interrupt();
        statStore.close();
    }
}
