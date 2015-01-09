
package com.tc.trident.core;

import java.io.Serializable;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.Map;

/**
 * TODO 类的功能描述。
 *
 * @author kozz.gaof
 * @date Dec 12, 2014 1:48:29 PM
 * @id $Id$
 */
public class Transaction implements StatInfo, Serializable {
    
    private static final long serialVersionUID = 8339698699597617795L;
    
    private long beginTime = 0;
    
    private long endTime = 0;
    
    private boolean success = false;
    
    private String name;
    
    private ArrayList<Transaction> childTransactions;
    
    private Object[] attachments;
    
    private static final String URL = "url";
    
    private static final String BEGIN = "begin";
    
    private static final String END = "end";
    
    private static final String STATUS = "status";
    
    private static final String CHILDREN = "children";
    
    private static final String ATTACHMENTS = "attachments";
    
    public long getBeginTime() {
    
        return beginTime;
    }
    
    public long getEndTime() {
    
        return endTime;
    }
    
    public boolean isSuccess() {
    
        return success;
    }
    
    public void setSuccess(boolean success) {
    
        this.success = success;
    }
    
    public String getName() {
    
        return name;
    }
    
    public ArrayList<Transaction> getChildTransactions() {
    
        return childTransactions;
    }
    
    public Object[] getAttachments() {
    
        return attachments;
    }
    
    public Transaction(String name, Object... attachments) {
    
        beginTime = System.currentTimeMillis();
        this.name = name;
        this.attachments = attachments;
    }
    
    /**
     * 开启一个执行事务。<b>必须确保和<{@link #submit()}>方法结对出现！</b>
     */
    public void begin() {
    
        StatContext context = StatContext.currentContext();
        context.currentTransaction().addTransaction(this);
        context.pushTransaction(this);
    }
    
    /**
     * 提交一个执行事务。<b>必须确保和<{@link #begin()}>方法结对出现！</b>
     */
    public void submit() {
    
        StatContext context = StatContext.currentContext();
        context.popTransaction();
        endTime = System.currentTimeMillis();
    }
    
    public void addTransaction(Transaction t) {
    
        if (childTransactions == null) {
            childTransactions = new ArrayList<Transaction>();
        }
        childTransactions.add(t);
    }
    
    @Override
    public Map<String, Object> compact() {
    
        HashMap<String, Object> map = new HashMap<String, Object>();
        map.put(URL, name);
        map.put(BEGIN, beginTime);
        map.put(END, endTime);
        map.put(STATUS, (success ? "S" : "F"));
        if (childTransactions != null && childTransactions.size() > 0) {
            ArrayList<Map<String, ?>> ct = new ArrayList<Map<String, ?>>();
            for (Transaction t : childTransactions) {
                ct.add(t.compact());
            }
            map.put(CHILDREN, ct);
        }
        if (attachments != null && attachments.length > 0) {
            ArrayList<Object> at = new ArrayList<Object>();
            for (Object a : at) {
                at.add(a);
            }
            map.put(ATTACHMENTS, at);
        }
        
        return map;
    }
    
    @Override
    public String toString() {
    
        StringBuffer result = new StringBuffer();
        result.append("[T]: " + name);
        result.append(" [E]: " + (endTime - beginTime));
        result.append(" [S]: " + (success ? "S" : "F"));
        result.append(" [B]: " + beginTime);
        result.append(" [F]: " + endTime);
        return result.toString();
    }
}
