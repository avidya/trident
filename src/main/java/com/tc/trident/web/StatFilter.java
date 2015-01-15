
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
import com.tc.trident.store.StatStore;
import com.tc.trident.util.HostUtils;

/**
 * This filter is supposed to intercept before any other ones.
 * 
 * <p>
 * When in init phase, this filter will attempt to initialize a StatStore instance specified in web.xml, such StatStore
 * implementation MUST provide a constructor without parameters.
 * 
 * <p>
 * For each request, one correspond StatContext will be instantiated in ThreadLocal for any consequent transactions to
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
            Class<?> statStoreClass = Class.forName(storeName, true, Thread.currentThread().getContextClassLoader());
            logger.info("Loading StatStore class: " + statStoreClass);
            statStore = (StatStore) statStoreClass.newInstance();
            statStore.init();
            this.state = true;
            logger.info("Finish initializing StatStore. ");
            
            loadStatCollectorIfAvailable();
        } catch (ClassNotFoundException | InstantiationException | IllegalAccessException e) {
            this.state = false;
            throw new ServletException("Failed to load StatStore, please check the configuration of filter in web.xml", e);
        } catch (TridentException e) {
            this.state = false;
            throw new ServletException("Failed in initializing StatStore", e);
        }
    }
    
    private void loadStatCollectorIfAvailable() {
    
        try {
            Class<?> collectorClass = Class.forName("com.tc.trident.vmstatus.StatCollector");
            Method setStatStoreMethod = collectorClass.getDeclaredMethod("setStatStore", com.tc.trident.store.StatStore.class);
            final Object collector = collectorClass.newInstance();
            
            setStatStoreMethod.invoke(collector, statStore);
            Runtime.getRuntime().addShutdownHook(new Thread() {
                
                @Override
                public void run() {
                
                    try {
                        ((Closeable) collector).close();
                    } catch (IOException e) {
                        // TODO Auto-generated catch block
                        e.printStackTrace();
                    }
                }
            });
            new Thread((Runnable) collector).start();
        } catch (ClassNotFoundException ex) {
            System.out.println("==========> no StatCollector found. JVM status won't be collected.");
        } catch (InstantiationException | IllegalAccessException |
                NoSuchMethodException | SecurityException |
                IllegalArgumentException | InvocationTargetException e) {
            e.printStackTrace();
        }
    }
    
    @Override
    public void doFilter(ServletRequest request, ServletResponse response, FilterChain chain) throws IOException, ServletException {
    
        if (state) {
            Transaction t = null;
            
            if (request instanceof HttpServletRequest) {
                HttpServletRequest r = (HttpServletRequest) request;
                boolean isAsyncRequest = r.getHeader(ASYNC_HEADER) != null;
                String requestPath = r.getContextPath() + r.getServletPath();
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
