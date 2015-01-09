
package com.tc.trident.store;

import com.tc.trident.core.StatInfo;
import com.tc.trident.core.TridentException;

/**
 * Interface for storing statistics information.
 *
 * @author kozz.gaof
 * @date Dec 12, 2014 1:54:59 PM
 * @id $Id$
 */
public interface StatStore {
    
    /**
     * to persist StatInfo
     *
     * @param statInfo
     */
    void store(StatInfo statInfo) throws TridentException;
    
    void init() throws TridentException;
    
    void close() throws TridentException;
    
}
