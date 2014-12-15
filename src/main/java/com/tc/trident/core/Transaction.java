
package com.tc.trident.core;

import java.io.Serializable;
import java.util.ArrayList;

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
    
    /**
     * {@inheritDoc}
     */
    @Override
    public String getStatInfo() {
    
        // TODO Auto-generated method stub
        return null;
    }
    
    @Override
    public String toString() {
    
        String elapse = endTime == 0 ? "N/A" : (endTime - beginTime) + " ms";
        StringBuffer result = new StringBuffer();
        result.append("[T]: " + name);
        result.append(" [E]: " + elapse);
        result.append(" [S]: " + (success ? "S" : "F"));
        return result.toString();
    }
}
