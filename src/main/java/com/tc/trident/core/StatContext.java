
package com.tc.trident.core;

import java.io.Serializable;
import java.util.Stack;

/**
 * TODO 类的功能描述。
 *
 * @author kozz.gaof
 * @date Dec 12, 2014 1:43:45 PM
 * @id $Id$
 */
public class StatContext implements StatInfo, Serializable {
    
    /** TODO 字段含义 */
    
    private static final long serialVersionUID = -3973541459226247268L;
    
    public static final String GLOBAL = "GLOBAL";
    
    private static final ThreadLocal<StatContext> contextLocal = new ThreadLocal<StatContext>() {
        
        @Override
        public StatContext initialValue() {
        
            return new StatContext(GLOBAL);
        }
    };
    
    private Stack<Transaction> transactionStack;
    
    public StatContext(String name) {
    
        this(new Transaction(name));
    }
    
    public StatContext(Transaction defaultTransaction) {
    
        transactionStack = new Stack<Transaction>();
        transactionStack.push(defaultTransaction == null ? new Transaction(GLOBAL) : defaultTransaction);
    }
    
    public void finish() {
    
        Transaction t = currentTransaction();
        t.setSuccess(true);
        t.submit();
    }
    
    public static StatContext currentContext() {
    
        return contextLocal.get();
    }
    
    public static void setCurrentContext(StatContext sc) {
    
        contextLocal.set(sc);
    }
    
    public Transaction currentTransaction() {
    
        return transactionStack.get(transactionStack.size() - 1);
    }
    
    protected void pushTransaction(Transaction t) {
    
        this.transactionStack.push(t);
    }
    
    protected void popTransaction() {
    
        if (transactionStack.size() > 1) { // keep the global transaction
            this.transactionStack.pop();
        }
    }
    
    /**
     * {@inheritDoc}
     */
    @Override
    public String compact() {
    
        return currentTransaction().compact();
    }
    
}
