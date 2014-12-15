package com.tc.trident.core;


/**
 * TODO 类的功能描述。
 *
 * @author kozz.gaof
 * @date Dec 12, 2014 7:45:04 PM
 * @id $Id$
 */
public class TridentException extends Exception{

    /** TODO 字段含义 */
    
    private static final long serialVersionUID = -5375496092482484859L;
    
    public TridentException(String msg) {
        
        super(msg);
    }
    
    public TridentException(String msg, Throwable cause) {
    
        super(msg, cause);
    }
    
    public TridentException(Throwable cause) {
    
        super(cause);
    }
}
