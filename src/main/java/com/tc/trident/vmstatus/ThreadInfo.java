
package com.tc.trident.vmstatus;

/**
 *
 * @author kozz.gaof
 * @date Jan 19, 2015 7:06:52 PM
 * @id $Id$
 */
public class ThreadInfo {
    
    // active thread count
    private int active;
    
    // daemon thread count
    private int daemon;
    
    private int peek;
    
    /**
     * http thread count
     * Recognized through characteristic name specified by Servlet container
     * i.e. http-xxx for tomcat and qtpxxx for jetty.
     */
    private int http;
    
    public int getActive() {
    
        return active;
    }
    
    public void setActive(int active) {
    
        this.active = active;
    }
    
    public int getDaemon() {
    
        return daemon;
    }
    
    public void setDaemon(int daemon) {
    
        this.daemon = daemon;
    }
    
    public int getPeek() {
    
        return peek;
    }
    
    public void setPeek(int peek) {
    
        this.peek = peek;
    }
    
    public int getHttp() {
    
        return http;
    }
    
    public void setHttp(int http) {
    
        this.http = http;
    }
    
    @Override
    public String toString() {
    
        return "ThreadInfo [active=" + active + ", daemon=" + daemon + ", peek=" + peek + ", http=" + http + "]";
    }
    
}
