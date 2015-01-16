
package com.tc.trident.core;

import java.io.Serializable;
import java.util.Map;
import java.util.Stack;

/**
 *
 * @author kozz.gaof
 * @date Dec 12, 2014 1:43:45 PM
 * @id $Id$
 */
public class StatContext implements StatInfo, Serializable {
    
    private static final long serialVersionUID = -3973541459226247268L;
    
    public static final String GLOBAL = "GLOBAL";
    
    private static final ThreadLocal<StatContext> contextLocal = new ThreadLocal<StatContext>();
    
    private Stack<Transaction> transactionStack;
    
    private String appName;
    
    private String hostIP;
    
    private String hostName;
    
    public void setAppName(String appName) {
    
        this.appName = appName;
    }
    
    public void setHostIP(String hostIP) {
    
        this.hostIP = hostIP;
    }
    
    public void setHostName(String hostName) {
    
        this.hostName = hostName;
    }
    
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
    
    public void clear() {
    
        contextLocal.remove();
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
    
        if (transactionStack.size() > 1) { // keep, at least, one global transaction
            this.transactionStack.pop();
        }
    }
    
    @Override
    public Map<String, Object> compact() {
    
        if (transactionStack.size() < 1) {
            throw new IllegalStateException("compact in an empty StatContext");
        }
        Transaction t = transactionStack.get(0);
        Map<String, Object> map = t.compact();
        map.put(HOSTNAME, hostName);
        map.put(HOSTIP, hostIP);
        map.put(APPNAME, appName);
        return map;
    }
    
    @Override
    public String toString() {
    
        StringBuffer result = new StringBuffer();
        result.append("{Hostname: " + hostName);
        result.append(", IP: " + hostIP);
        result.append("} - ");
        if (transactionStack.size() > 0) {
            Transaction t = transactionStack.get(0);
            result.append(t.toString());
        }
        return result.toString();
    }
    
}
