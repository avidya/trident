
package com.tc.trident.web;

import java.io.Serializable;
import java.util.Map;

import com.tc.trident.core.Transaction;

/**
 * An specific Transacation designed for WEB request only.
 *
 * @author kozz.gaof
 * @date Dec 16, 2014 3:25:07 PM
 * @id $Id$
 */
public class WebRequest extends Transaction implements Serializable {
    
    private static final long serialVersionUID = 1563266726039488172L;
    
    public static final String ASYNC = "async";
    
    private boolean isAsyncRequest;
    
    public WebRequest(String name, Object[] attachments) {
    
        super(name, attachments);
    }
    
    public boolean isAsyncRequest() {
    
        return isAsyncRequest;
    }
    
    public void setAsyncRequest(boolean isAsyncRequest) {
    
        this.isAsyncRequest = isAsyncRequest;
    }
    
    @Override
    public Map<String, Object> compact() {
    
        Map<String, Object> map = super.compact();
        map.put(ASYNC, isAsyncRequest);
        return map;
    }
    
    @Override
    public String toString() {
    
        return super.toString() + " [A] : " + isAsyncRequest;
    }
    
}
