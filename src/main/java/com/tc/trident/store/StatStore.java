package com.tc.trident.store;

import com.tc.trident.core.StatInfo;
import com.tc.trident.core.TridentException;


/**
 * TODO 类的功能描述。
 *
 * @author kozz.gaof
 * @date Dec 12, 2014 1:54:59 PM
 * @id $Id$
 */
public interface StatStore {
    
    /**
     * 
     * 持久化统计信息
     *
     * @param statInfo
     */
    void store(StatInfo statInfo) throws TridentException;
    
    void init() throws TridentException;
    
    void close() throws TridentException;
    
}
