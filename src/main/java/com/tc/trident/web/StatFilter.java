
package com.tc.trident.web;

import java.io.Closeable;
import java.io.IOException;
import java.lang.reflect.InvocationTargetException;
import java.lang.reflect.Method;

import javax.servlet.Filter;
import javax.servlet.FilterChain;
import javax.servlet.FilterConfig;
import javax.servlet.ServletException;
import javax.servlet.ServletRequest;
import javax.servlet.ServletResponse;
import javax.servlet.http.HttpServletRequest;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import com.tc.trident.core.StatContext;
import com.tc.trident.core.Transaction;
import com.tc.trident.core.TridentException;
import com.tc.trident.core.conf.Configuration;
import com.tc.trident.store.QueueStatStore;
import com.tc.trident.store.StatStore;
import com.tc.trident.util.HostUtils;

/**
 * This filter is supposed to intercept before any target class to get working.
 * 
 * <p>
 * When in init phase, this filter will attempt to initialize a StatStore instance specified in web.xml, such StatStore
 * implementation MUST provide a constructor without parameters.
 * 
 * <p>
 * For each request, a correspond StatContext will be instantiated in ThreadLocal for any consequent transactions to
 * attach to.
 * 
 * @author kozz.gaof
 * @date Dec 12, 2014 10:15:51 AM
 * @id $Id$
 */
public class StatFilter implements Filter {
    
    private Logger logger = LoggerFactory.getLogger(StatFilter.class);
    
    private static final String ASYNC_HEADER = "X-Requested-With";
    
    private static final String STORE_NAME = "statStore";
    
    private static final String HOSTNAME = HostUtils.getLocalHostName();
    
    private static final String HOSTIP = HostUtils.getHostIP();
    
    private StatStore statStore;
    
    private boolean state = false;
    
    @Override
    public void init(FilterConfig filterConfig) throws ServletException {
    
        try {
            
            String storeName = filterConfig.getInitParameter(STORE_NAME);
            if (storeName != null) {
                
                statStore = loadStatStore(storeName);
                
                // queue name is required for QueueStatStore.
                if (QueueStatStore.class.isAssignableFrom(statStore.getClass())) {
                    ((QueueStatStore) statStore).setQueueName(Configuration.PERFORMANCE_QUEUE_NAME);
                }
                this.state = true;
                logger.info(">>>>>>>>>>> Finish initializing StatStore. ");
                
                startStatCollectorIfAvailable(storeName);
            }
        } catch (TridentException e) {
            this.state = false;
            logger.warn("Failed in initializing StatStore", e);
        }
    }
    
    private StatStore loadStatStore(String storeClass) throws TridentException, ServletException {
    
        try {
            Class<?> statStoreClass = Class.forName(storeClass, true, Thread.currentThread().getContextClassLoader());
            logger.info(">>>>>>>>>>> Loading StatStore class: " + statStoreClass);
            StatStore statStore = (StatStore) statStoreClass.newInstance();
            statStore.init();
            return statStore;
        } catch (ClassNotFoundException | InstantiationException | IllegalAccessException e) {
            throw new ServletException("Failed to load StatStore, please check the configuration of filter in web.xml", e);
        }
    }
    
    /**
     * start the StatCollector, if we could find it in classpath.
     * 
     * @param storeName
     * @throws TridentException
     * @throws ServletException
     */
    private void startStatCollectorIfAvailable(String storeName) throws TridentException, ServletException {
    
        try {
            Class<?> collectorClass = Class.forName("com.tc.trident.vmstatus.StatCollector");
            final Object collector = collectorClass.newInstance();
            
            StatStore statStore = loadStatStore(storeName);
            
            // queue name is required for QueueStatStore.
            if (QueueStatStore.class.isAssignableFrom(statStore.getClass())) {
                ((QueueStatStore) statStore).setQueueName(Configuration.STATUS_QUEUE_NAME);
            }
            
            // since StatCollector is absent at compile time, reflection is required for invoking target methods.
            Method setStatStoreMethod = collectorClass.getDeclaredMethod("setStatStore", com.tc.trident.store.StatStore.class);
            setStatStoreMethod.invoke(collector, statStore);
            
            Runtime.getRuntime().addShutdownHook(new Thread() {
                
                @Override
                public void run() {
                
                    try {
                        ((Closeable) collector).close();
                    } catch (IOException e) {
                        e.printStackTrace();
                    }
                }
            });
            
            Thread collectorThread = (Thread) collector;
            collectorThread.setName("JVM runtime information collector [StatCollector]");
            collectorThread.start();
            
        } catch (ClassNotFoundException ex) {
            logger.info(">>>>>>>>>>> no StatCollector founded. JVM status won't be collected.");
        } catch (InstantiationException | IllegalAccessException |
                NoSuchMethodException | SecurityException |
                IllegalArgumentException | InvocationTargetException e) {
            logger.error("==========> Error in starting StatCollector.", e);
        }
    }
    
    @Override
    public void doFilter(ServletRequest request, ServletResponse response, FilterChain chain) throws IOException, ServletException {
    
        if (state) {
            Transaction t = null;
            
            if (request instanceof HttpServletRequest) {
                HttpServletRequest httpServletRequest = (HttpServletRequest) request;
                boolean isAsyncRequest = httpServletRequest.getHeader(ASYNC_HEADER) != null;
                String requestPath = httpServletRequest.getContextPath() + httpServletRequest.getServletPath();
                Object[] parameters = request.getParameterMap().values().toArray();
                WebRequest webRequest = new WebRequest(requestPath, parameters);
                webRequest.setAsyncRequest(isAsyncRequest);
                t = webRequest;
            } else {
                t = new Transaction(StatContext.GLOBAL);
            }
            
            StatContext context = new StatContext(t);
            context.setAppName(Configuration.APP_NAME);
            context.setHostIP(HOSTIP);
            context.setHostName(HOSTNAME);
            StatContext.setCurrentContext(context);
            
            try {
                chain.doFilter(request, response);
                context.finish();
                statStore.store(context);
            } catch (TridentException e) {
                logger.error("==========> Failed in store statistics info! " + context, e);
            } finally {
                context.clear();
            }
        } else {
            chain.doFilter(request, response);
        }
        
    }
    
    @Override
    public void destroy() {
    
        if (statStore != null) {
            try {
                statStore.close();
            } catch (IOException e) {
                logger.error("==========> Failed in closing StatStore! ", e);
            }
        }
    }
    
}
