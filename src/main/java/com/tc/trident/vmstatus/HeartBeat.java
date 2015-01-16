
package com.tc.trident.vmstatus;

import java.util.HashMap;
import java.util.Map;

import com.dianping.cat.status.model.entity.MemoryInfo;
import com.dianping.cat.status.model.entity.ThreadsInfo;
import com.tc.trident.core.StatInfo;
import com.tc.trident.core.conf.Configuration;

/**
 *
 * @author kozz.gaof
 * @date Jan 13, 2015 2:17:13 PM
 * @id $Id$
 */
public class HeartBeat implements StatInfo {
    
    private String hostname;
    
    private String ip;
    
    private MemoryInfo memoryInfo;
    
    private ThreadsInfo threadsInfo;
    
    public HeartBeat(String hostname, String ip) {
    
        this.hostname = hostname;
        this.ip = ip;
    }
    
    public void setMemoryInfo(MemoryInfo memoryInfo) {
    
        this.memoryInfo = memoryInfo;
    }
    
    public void setThreadsInfo(ThreadsInfo threadsInfo) {
    
        this.threadsInfo = threadsInfo;
    }
    
    @Override
    public Map<String, Object> compact() {
    
        HashMap<String, Object> heartBeat = new HashMap<String, Object>();
        heartBeat.put(HOSTNAME, hostname);
        heartBeat.put(HOSTIP, ip);
        heartBeat.put(APPNAME, Configuration.APP_NAME);
        heartBeat.put("memory", memoryInfo);
        heartBeat.put("threads", threadsInfo);
        return heartBeat;
    }
    
}
