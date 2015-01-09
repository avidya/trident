
package com.tc.trident.store;

import java.util.LinkedList;
import java.util.List;
import java.util.concurrent.locks.ReentrantLock;

import com.tc.trident.core.StatInfo;
import com.tc.trident.core.conf.Configuration;

/**
 *
 * @author kozz.gaof
 * @date Dec 12, 2014 4:36:33 PM
 * @id $Id$
 */
public abstract class AbstractAsyncBatchStatStore extends AbstractAsyncStatStore {
    
    public static final Integer DEFAULT_THRESHOLD = 20;
    
    protected List<StatInfo> queueStatInfo = new LinkedList<StatInfo>();
    
    private ReentrantLock queueLock = new ReentrantLock();
    
    private void queue(StatInfo statInfo) {
    
        queueStatInfo.add(statInfo);
    }
    
    private Integer getThreshold() {
    
        try {
            Integer t = Integer.parseInt(Configuration.LOCAL_QUEUE_SIZE);
            return t;
        } catch (NumberFormatException e) {
            return DEFAULT_THRESHOLD;
        }
    }
    
    public abstract void flush();
    
    @Override
    void doStore(StatInfo statInfo) {
    
        try {
            queueLock.lock();
            queue(statInfo);
            if (queueStatInfo.size() >= getThreshold()) {
                flush();
                queueStatInfo.clear();
            }
        } finally {
            queueLock.unlock();
        }
    }
}
