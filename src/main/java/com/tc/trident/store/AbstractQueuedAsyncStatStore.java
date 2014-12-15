
package com.tc.trident.store;

import java.util.LinkedList;
import java.util.List;

import com.tc.trident.core.StatInfo;

/**
 * TODO 类的功能描述。
 *
 * @author kozz.gaof
 * @date Dec 12, 2014 4:36:33 PM
 * @id $Id$
 */
public abstract class AbstractQueuedAsyncStatStore extends AbstractAsyncStatStore {
    
    public static final Integer VALVE = 20;
    
    private List<StatInfo> queueStatInfo = new LinkedList<StatInfo>();
    
    synchronized void queue(StatInfo statInfo){
        queueStatInfo.add(statInfo);
    }
    
    abstract void flush(List<StatInfo> statInfo);   
    
    @Override
    synchronized void doStore(StatInfo statInfo) {
        if(queueStatInfo.size() > VALVE){
            flush(queueStatInfo);
            queueStatInfo.clear();
        }
        queue(statInfo);
    }
    
}
