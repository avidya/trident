
package com.tc.trident.web;

import java.io.IOException;

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
import com.tc.trident.core.web.WebRequest;
import com.tc.trident.store.StatStore;

/**
 * TODO 类的功能描述。
 *
 * @author kozz.gaof
 * @date Dec 12, 2014 10:15:51 AM
 * @id $Id$
 */
public class StatFilter implements Filter {
    
    private Logger logger = LoggerFactory.getLogger(StatFilter.class);
    
    private static final String ASYNC_HEADER = "X-Requested-With";
    
    private static final String STORE_NAME = "statStore";
    
    private StatStore statStore;
    
    private boolean state = false;
    
    @Override
    public void init(FilterConfig filterConfig) throws ServletException {
    
        try {
            @SuppressWarnings("rawtypes")
            Class statStoreClass = Class.forName(filterConfig.getInitParameter(STORE_NAME), true, Thread.currentThread().getContextClassLoader());
            logger.info("Loading StatStore class: " + statStoreClass);
            statStore = (StatStore) statStoreClass.newInstance();
            statStore.init();
            this.state = true;
            logger.info("Finish initializing StatStore. ");
        } catch (ClassNotFoundException | InstantiationException | IllegalAccessException e) {
            this.state = false;
            throw new ServletException("Failed to load StatStore, please check the configuration of filter in web.xml", e);
        } catch (TridentException e) {
            this.state = false;
            throw new ServletException("Failed in initializing StatStore", e);
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
            StatContext.setCurrentContext(context);
            chain.doFilter(request, response);
            try {
                statStore.store(context);
            } catch (TridentException e) {
                logger.error("Failed in store statistics info! ", e);
            } finally {
                context.finish();
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
            } catch (TridentException e) {
                logger.error("Failed in closing StatStore! ", e);
            }
        }
    }
    
}
