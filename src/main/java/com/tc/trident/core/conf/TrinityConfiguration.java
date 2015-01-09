
package com.tc.trident.core.conf;

import java.util.Properties;

import org.apache.commons.lang3.StringUtils;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import com.tc.trident.core.Constants;
import com.tc.trinity.core.AbstractConfigurable;
import com.tc.trinity.core.ConfigContext;

/**
 * trinity configuration system supported
 *
 * @author kozz.gaof
 * @date Jan 2, 2015 2:14:59 PM
 * @id $Id$
 */
public class TrinityConfiguration extends AbstractConfigurable {
    
    private static final Logger logger = LoggerFactory.getLogger(TrinityConfiguration.class);
    
    @Override
    public String getName() {
    
        return "trident";
    }
    
    @Override
    public String getExtensionName() {
    
        return this.getClass().getName();
    }
    
    @Override
    protected boolean doInit(ConfigContext configContext, Properties properties) {
    
        try {
            Class.forName(Constants.CONFIGURATION_CLASS, false, this.getClass().getClassLoader());
            if (StringUtils.isBlank(Configuration.BROKER_URL)) {
                Configuration.BROKER_URL = properties.getProperty(Constants.BROKER_URL);
            }
            if (StringUtils.isBlank(Configuration.BROKER_PORT)) {
                Configuration.BROKER_PORT = properties.getProperty(Constants.BROKER_PORT);
            }
            if (StringUtils.isBlank(Configuration.BROKER_USERNAME)) {
                Configuration.BROKER_USERNAME = properties.getProperty(Constants.BROKER_USERNAME);
            }
            if (StringUtils.isBlank(Configuration.BROKER_PASSWORD)) {
                Configuration.BROKER_PASSWORD = properties.getProperty(Constants.BROKER_PASSWORD);
            }
            if (StringUtils.isBlank(Configuration.QUEUE_NAME)) {
                Configuration.QUEUE_NAME = properties.getProperty(Constants.QUEUE_NAME);
            }
            if (StringUtils.isBlank(Configuration.LOCAL_QUEUE_SIZE)) {
                Configuration.LOCAL_QUEUE_SIZE = properties.getProperty(Constants.LOCAL_QUEUE_SIZE);
            }
            if (StringUtils.isBlank(Configuration.APP_NAME)) {
                Configuration.APP_NAME = properties.getProperty(Constants.APP_NAME);
            }
        } catch (ClassNotFoundException e) {
            logger.error("", e);
            return false;
        }
        
        return true;
    }
    
    @Override
    protected boolean doOnChange(String key, String value, String originalValue) {
    
        if (key.equals(Configuration.LOCAL_QUEUE_SIZE)) {
            Configuration.LOCAL_QUEUE_SIZE = value;
            return true;
        }
        return false;
    }
    
}
