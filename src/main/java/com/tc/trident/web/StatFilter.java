
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
import com.tc.trident.core.TridentException;
import com.tc.trident.core.web.WebRequest;
import com.tc.trident.store.SimpleFileStatStore;
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
    
    private StatStore statStore;
    
    private boolean state = true;
    
    @Override
    public void init(FilterConfig filterConfig) throws ServletException {
    
        // TODO 需要获取具体的statStore
        statStore = new SimpleFileStatStore();
        try {
            statStore.init();
        } catch (TridentException e) {
            logger.warn("Failed in initializing StatStore", e);
            this.state = false;
            // ApplicationContext ac =
            // WebApplicationContextUtils.getWebApplicationContext(filterConfig.getServletContext());
            // if (ac != null) {
            // }
        }
    }
    
    @Override
    public void doFilter(ServletRequest request, ServletResponse response, FilterChain chain) throws IOException, ServletException {
    
        if (state) {
            HttpServletRequest r = (HttpServletRequest) request;
            boolean isAsyncRequest = r.getHeader("X-Requested-With") != null;
            String requestPath = r.getContextPath() + r.getServletPath();
            Object[] parameters = request.getParameterMap().values().toArray();
            WebRequest webRequest = new WebRequest(requestPath, parameters);
            webRequest.setAsyncRequest(isAsyncRequest);
            StatContext context = new StatContext(requestPath, webRequest);
            StatContext.setCurrentContext(context);
            chain.doFilter(request, response);
            try {
                statStore.store(context);
            } catch (TridentException e) {
                // TODO Auto-generated catch block
                e.printStackTrace();
            } finally {
                context.finish();
            }
        } else {
            chain.doFilter(request, response);
        }
        
    }
    
    /**
     * {@inheritDoc}
     */
    @Override
    public void destroy() {
    
        if (statStore != null) {
            try {
                statStore.close();
            } catch (TridentException e) {
                // TODO Auto-generated catch block
                e.printStackTrace();
            }
        }
    }
    
}
