package com.tc.trident.core.web;

import com.tc.trident.core.Transaction;


/**
 * TODO 类的功能描述。
 *
 * @author kozz.gaof
 * @date Dec 16, 2014 3:25:07 PM
 * @id $Id$
 */
public class WebRequest extends Transaction{

    private static final long serialVersionUID = 1563266726039488172L;
    
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
    
}
