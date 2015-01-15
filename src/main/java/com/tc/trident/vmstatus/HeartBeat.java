
package com.tc.trident.vmstatus;

import java.util.HashMap;
import java.util.Map;

import com.dianping.cat.status.model.entity.MemoryInfo;
import com.dianping.cat.status.model.entity.ThreadsInfo;
import com.tc.trident.core.StatInfo;

/**
 * TODO 类的功能描述。
 *
 * @author kozz.gaof
 * @date Jan 13, 2015 2:17:13 PM
 * @id $Id$
 */
public class HeartBeat implements StatInfo {
    
    private MemoryInfo memoryInfo;
    
    private ThreadsInfo threadsInfo;
    
    public HeartBeat(MemoryInfo memoryInfo, ThreadsInfo threadsInfo) {
    
        this.memoryInfo = memoryInfo;
        this.threadsInfo = threadsInfo;
    }
    
    @Override
    public Map<String, Object> compact() {
    
        HashMap<String, Object> heartBeat = new HashMap<String, Object>();
        heartBeat.put("memory", memoryInfo);
        heartBeat.put("threads", threadsInfo);
        return heartBeat;
    }
    
}
