
package com.tc.trident.store.jms;

import java.util.List;

import org.springframework.jms.core.JmsTemplate;

import com.tc.trident.core.StatInfo;
import com.tc.trident.core.TridentException;
import com.tc.trident.store.AbstractAsyncBatchStatStore;

/**
 * TODO 类的功能描述。
 *
 * @author kozz.gaof
 * @date Dec 29, 2014 2:43:03 PM
 * @id $Id$
 */
public class JMSStatStore extends AbstractAsyncBatchStatStore {
    
    private JmsTemplate jmsTemplate;
    
    private String queueName;
    
    public void setJmsTemplate(JmsTemplate jmsTemplate) {
    
        this.jmsTemplate = jmsTemplate;
    }
    
    public void setQueueName(String queueName) {
    
        this.queueName = queueName;
    }
    
    @Override
    public void init() throws TridentException {
    
        // TODO Auto-generated method stub
        
    }
    
    @Override
    public void close() throws TridentException {
    
        // TODO Auto-generated method stub
        
    }
    
    /**
     * {@inheritDoc}
     */
    @Override
    public void flush(List<StatInfo> statInfo) {
    
        for (StatInfo info : statInfo) {
            jmsTemplate.convertAndSend(queueName, info);
        }
    }
    
}
