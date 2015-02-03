
package com.tc.trident.vmstatus;

import java.util.HashMap;
import java.util.List;
import java.util.Map;

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
    
    private Long timestamp;
    
    private MemoryInfo memoryInfo;
    
    private ThreadInfo threadInfo;
    
    private List<GCInfo> gcInfoList;
    
    public HeartBeat(String hostname, String ip) {
    
        this.hostname = hostname;
        this.ip = ip;
        timestamp = System.currentTimeMillis();
    }
    
    public void setMemoryInfo(MemoryInfo memoryInfo) {
    
        this.memoryInfo = memoryInfo;
    }
    
    public void setThreadsInfo(ThreadInfo threadsInfo) {
    
        this.threadInfo = threadsInfo;
    }
    
    public List<GCInfo> getGcInfoList() {
    
        return gcInfoList;
    }
    
    public void setGcInfoList(List<GCInfo> gcInfoList) {
    
        this.gcInfoList = gcInfoList;
    }
    
    @Override
    public Map<String, Object> compact() {
    
        HashMap<String, Object> heartBeat = new HashMap<String, Object>();
        heartBeat.put(HOSTNAME, hostname);
        heartBeat.put(HOSTIP, ip);
        heartBeat.put(APPNAME, Configuration.APP_NAME);
        heartBeat.put("memory", memoryInfo);
        heartBeat.put("thread", threadInfo);
        heartBeat.put("gcinfo", gcInfoList);
        heartBeat.put("timestamp", timestamp);
        return heartBeat;
    }
    
}
