
package com.tc.trident.vmstatus;

/**
 *
 * @author kozz.gaof
 * @date Jan 19, 2015 7:05:27 PM
 * @id $Id$
 */
public class MemoryInfo {
    
    // this one will be a little smaller than the value specified by -Xmx
    private long maxHeap;
    
    // heap usage
    private long usedHeap;
    
    // this one is controlled by -XX:MaxPermSize, but a little bigger than the specified one.
    private long maxNonHeap;
    
    // also a little bigger
    private long usedNonHeap;
    
    public long getMaxHeap() {
    
        return maxHeap;
    }
    
    public void setMaxHeap(long maxHeap) {
    
        this.maxHeap = maxHeap;
    }
    
    public long getUsedHeap() {
    
        return usedHeap;
    }
    
    public void setUsedHeap(long usedHeap) {
    
        this.usedHeap = usedHeap;
    }
    
    public long getMaxNonHeap() {
    
        return maxNonHeap;
    }
    
    public void setMaxNonHeap(long maxNonHeap) {
    
        this.maxNonHeap = maxNonHeap;
    }
    
    public long getUsedNonHeap() {
    
        return usedNonHeap;
    }
    
    public void setUsedNonHeap(long usedNonHeap) {
    
        this.usedNonHeap = usedNonHeap;
    }
    
}
