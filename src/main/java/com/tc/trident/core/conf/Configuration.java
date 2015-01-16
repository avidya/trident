
package com.tc.trident.core.conf;

import java.io.InputStream;
import java.util.Properties;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import com.tc.trident.core.Constants;

/**
 * Class to hold configuration needed.
 *
 * @author kozz.gaof
 * @date Jan 2, 2015 1:55:58 PM
 * @id $Id$
 */
public class Configuration {
    
    private static final Logger logger = LoggerFactory.getLogger(Configuration.class);
    
    private static final String config_file = "trident.properties";
    
    public static String BROKER_URL;
    
    public static String BROKER_PORT;
    
    public static String BROKER_USERNAME;
    
    public static String BROKER_PASSWORD;
    
    public static String PERFORMANCE_QUEUE_NAME;
    
    public static String STATUS_QUEUE_NAME;
    
    public static String LOCAL_QUEUE_SIZE;
    
    public static String APP_NAME;
    
    static {
        InputStream in = Configuration.class.getClassLoader().getResourceAsStream(config_file);
        if (in != null) {
            try {
                Properties props = new Properties();
                props.load(in);
                BROKER_URL = props.getProperty(Constants.BROKER_URL);
                BROKER_PORT = props.getProperty(Constants.BROKER_PORT);
                BROKER_USERNAME = props.getProperty(Constants.BROKER_USERNAME);
                BROKER_PASSWORD = props.getProperty(Constants.BROKER_PASSWORD);
                PERFORMANCE_QUEUE_NAME = props.getProperty(Constants.PERFORMANCE_QUEUE_NAME);
                STATUS_QUEUE_NAME = props.getProperty(Constants.STATUS_QUEUE_NAME);
                LOCAL_QUEUE_SIZE = props.getProperty(Constants.LOCAL_QUEUE_SIZE);
                APP_NAME = props.getProperty(Constants.APP_NAME);
            } catch (Exception e) {
                logger.error("Error in loading trident.properties file", e);
            }
        }
    }
}
