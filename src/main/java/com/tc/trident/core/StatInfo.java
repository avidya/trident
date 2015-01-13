
package com.tc.trident.core;

import java.util.Map;

/**
 *
 * @author kozz.gaof
 * @date Dec 12, 2014 1:55:50 PM
 * @id $Id$
 */
public interface StatInfo {
    
    Map<String, Object> compact();
    
    /**
     * toString() is EXTREMELY USEFUL in debugging.
     * Redeclaring this method can be regarded as a reminder in implementation.
     *
     * @return
     */
    public abstract String toString();
}
