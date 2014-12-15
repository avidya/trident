
package com.tc.trident.store;

import com.tc.trident.core.StatInfo;

/**
 * TODO 类的功能描述。
 *
 * @author kozz.gaof
 * @date Dec 12, 2014 1:58:43 PM
 * @id $Id$
 */
public abstract class AbstractAsyncStatStore implements StatStore {
    
    abstract void doStore(StatInfo statInfo);
    
    public void store(final StatInfo statInfo) {
    
        new Thread() {
            
            public void run() {
            
                doStore(statInfo);
            }
        }.start();
    }
}
