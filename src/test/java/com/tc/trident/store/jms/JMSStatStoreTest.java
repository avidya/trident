package com.tc.trident.store.jms;

import static org.junit.Assert.assertTrue;

import java.io.IOException;
import java.net.UnknownHostException;

import org.apache.activemq.transport.stomp.Stomp;
import org.apache.activemq.transport.stomp.Stomp.Headers.Subscribe;
import org.apache.activemq.transport.stomp.StompConnection;
import org.apache.activemq.transport.stomp.StompFrame;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.test.context.ContextConfiguration;
import org.springframework.test.context.junit4.SpringJUnit4ClassRunner;

import com.tc.trident.core.TridentException;
import com.tc.trident.store.StatStore;


/**
 * TODO 类的功能描述。
 *
 * @author kozz.gaof
 * @date Dec 29, 2014 6:47:59 PM
 * @id $Id$
 */
@RunWith(SpringJUnit4ClassRunner.class)
@ContextConfiguration(locations = {"classpath:trident-test.xml"})
public class JMSStatStoreTest {
    
    private StatStore jmsStatStore;
    
    @Autowired
    public void setJmsStatStore(StatStore jmsStatStore) {
    
        this.jmsStatStore = jmsStatStore;
    }

    @Test
    public void testSend() throws Exception{
//        jmsStatStore.store(new StatInfo(){
//
//            @Override
//            public String getStatInfo() {
//            
//                return "TEST JMS";
//            }
//            
//        });
//        Thread.sleep(600000);
        StompConnection connection = new StompConnection();
        connection.open("10.1.11.214", 61613);
                 
//        connection.connect("system", "manager");
        connection.connect(null, null);
        
//        StompFrame connect = connection.receive();
//        if (!connect.getAction().equals(Stomp.Responses.CONNECTED)) {
//            throw new Exception ("Not connected");
//        }
                 
        connection.begin("tx1");
        connection.send("/queue/stat-info", "message1", "tx1", null);
        connection.send("/queue/stat-info", "message2", "tx1", null);
        connection.commit("tx1");
             
        connection.subscribe("/queue/stat-info", Subscribe.AckModeValues.CLIENT);
             
        connection.begin("tx2");
             
        StompFrame message = connection.receive();
        System.out.println(message.getBody());
        connection.ack(message, "tx2");
             
        message = connection.receive();
        System.out.println(message.getBody());
        connection.ack(message, "tx2");
     
        connection.commit("tx2");
                 
        connection.disconnect();
        assertTrue(true);
    }
}
