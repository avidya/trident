
package com.tc.trident.vmstatus;

/**
 *
 * @author kozz.gaof
 * @date Jan 19, 2015 7:11:34 PM
 * @id $Id$
 */
public class GCInfo {
    
    private String name;
    
    private long count;
    
    private long time;
    
    public String getName() {
    
        return name;
    }
    
    public void setName(String name) {
    
        this.name = name;
    }
    
    public long getCount() {
    
        return count;
    }
    
    public void setCount(long count) {
    
        this.count = count;
    }
    
    public long getTime() {
    
        return time;
    }
    
    public void setTime(long time) {
    
        this.time = time;
    }
    
    @Override
    public String toString() {
    
        return "GCInfo [name=" + name + ", count=" + count + ", time=" + time + "]";
    }
}
