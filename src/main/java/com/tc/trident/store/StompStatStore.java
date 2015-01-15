
package com.tc.trident.store;

import java.io.IOException;

import org.apache.activemq.transport.stomp.StompConnection;
import org.apache.commons.lang3.StringUtils;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import com.alibaba.fastjson.JSON;
import com.alibaba.fastjson.serializer.SerializerFeature;
import com.tc.trident.core.StatInfo;
import com.tc.trident.core.TridentException;
import com.tc.trident.core.conf.Configuration;

/**
 * TODO 类的功能描述。
 *
 * @author kozz.gaof
 * @date Jan 1, 2015 2:41:02 PM
 * @id $Id$
 */
public class StompStatStore extends AbstractAsyncBatchStatStore {
    
    private static final Logger logger = LoggerFactory.getLogger(StompStatStore.class);
    
    private StompConnection connection = new StompConnection();
    
    private Boolean closed = false;
    
    private static final String misConfMsg = "Error in intializing StompStatStore, please check the Configuration either in trident.properties or Configuration Center/Trinity";
    
    @Override
    public void init() throws TridentException {
    
        if (StringUtils.isBlank(Configuration.BROKER_URL)
                || StringUtils.isBlank(Configuration.BROKER_PORT)
                || StringUtils.isBlank(Configuration.QUEUE_NAME)) {
            logger.error(misConfMsg);
            throw new IllegalStateException(misConfMsg);
        }
        
        try {
            connection.open(Configuration.BROKER_URL, Integer.parseInt(Configuration.BROKER_PORT));
            connection.connect(Configuration.BROKER_USERNAME, Configuration.BROKER_PASSWORD);
        } catch (NumberFormatException e) {
            logger.error(misConfMsg);
            throw new IllegalStateException(misConfMsg);
        } catch (Exception e) {
            throw new TridentException(e);
        }
        
    }
    
    @Override
    public void close() throws IOException {
    
        try {
            if (!closed) {
                synchronized (closed) {
                    if (!closed) {
                        connection.close();
                        closed = true;
                    }
                }
            }
        } catch (IOException e) {
            logger.error("Error in closing StompConnection", e);
            throw e;
        }
    }
    
    @Override
    public void flush() {
    
        try {
            connection.begin("tx1");
            for (StatInfo stat : queueStatInfo) {
                connection.send("/queue/stat-info", JSON.toJSONString(stat.compact(), SerializerFeature.DisableCircularReferenceDetect), "tx1", null);
            }
            connection.commit("tx1");
        } catch (Exception e) {
            logger.warn("Error in pushing message to Broker, stat-info is discarding...", e);
        } finally {
            queueStatInfo.clear();
        }
    }
}
