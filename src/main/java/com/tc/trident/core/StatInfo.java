
package com.tc.trident.core;

import java.util.Map;

/**
 *
 * @author kozz.gaof
 * @date Dec 12, 2014 1:55:50 PM
 * @id $Id$
 */
public interface StatInfo {
    
    
    public static final String HOSTNAME = "hostname";
    
    public static final String APPNAME = "app";
    
    public static final String HOSTIP = "ip";
    
    
    Map<String, Object> compact();
    
    /**
     * toString() is EXTREMELY USEFUL in debugging.
     * Redeclaring this method can be regarded as a reminder in implementation.
     *
     * @return
     */
    public abstract String toString();
}
