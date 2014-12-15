
package com.tc.trident.spring;

import java.lang.reflect.Method;

import org.aopalliance.intercept.MethodInterceptor;
import org.aopalliance.intercept.MethodInvocation;

import com.tc.trident.core.Transaction;

/**
 * TODO 类的功能描述。
 *
 * @author kozz.gaof
 * @date Dec 12, 2014 4:51:54 PM
 * @id $Id$
 */
public class StatMethodInterceptor implements MethodInterceptor {
    
    /**
     * {@inheritDoc}
     */
    @Override
    public Object invoke(MethodInvocation i) throws Throwable {
    
        Method m = i.getMethod();
        String className = m.getDeclaringClass().getName();
        Transaction t = new Transaction(className + "." + m.getName(), i.getArguments());
        t.begin();
        try {
            Object ret = i.proceed();
            t.setSuccess(true);
            return ret;
        } catch (Throwable e) {
            t.setSuccess(false);
            throw e;
        } finally {
            t.submit();
        }
    }
}
