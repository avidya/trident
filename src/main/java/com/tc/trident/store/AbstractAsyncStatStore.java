
package com.tc.trident.store;

import java.util.concurrent.BlockingQueue;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;
import java.util.concurrent.LinkedBlockingQueue;
import java.util.concurrent.TimeUnit;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import com.tc.trident.core.StatInfo;

/**
 * Store StatInfo in an asynchronized way.
 * 
 * @author kozz.gaof
 * @date Dec 12, 2014 1:58:43 PM
 * @id $Id$
 */
public abstract class AbstractAsyncStatStore implements StatStore {
    
    private Logger logger = LoggerFactory.getLogger(AbstractAsyncStatStore.class);
    
    private static final Integer LOCAL_QUEUE_SIZE = 500;
    
    protected BlockingQueue<StatInfo> taskQueue = new LinkedBlockingQueue<StatInfo>(LOCAL_QUEUE_SIZE);
    
    private ExecutorService executor;
    
    abstract void doStore(StatInfo statInfo);
    
    public AbstractAsyncStatStore() {
    
        executor = Executors.newCachedThreadPool();
        executor.execute(new TaskExecutor());
    }
    
    public final void store(final StatInfo statInfo) {
    
        if (logger.isDebugEnabled()) {
            logger.debug(">>>>>>>>>> Attempt to store statistics info: " + statInfo);
        }
        try {
            if (!taskQueue.offer(statInfo, 50L, TimeUnit.MILLISECONDS)) {
                logger.warn("=========> Local storage queue is full! Discarding statistics info: " + statInfo);
            }
        } catch (InterruptedException e) {
            logger.warn("=========> Discarding statistics info: " + statInfo, e);
        }
    }
    
    private class TaskExecutor implements Runnable {
        
        @Override
        public void run() {
        
            for (;;) {
                try {
                    StatInfo statInfo = taskQueue.poll();
                    if (statInfo == null) {
                        // the queue is empty at present, we should give it a try 5 seconds later.
                        Thread.sleep(5000);
                    } else {
                        doStore(statInfo);
                    }
                } catch (Throwable t) {
                    logger.warn("=========> Error in storing statistics info. ", t);
                }
            }
        }
    }
}
