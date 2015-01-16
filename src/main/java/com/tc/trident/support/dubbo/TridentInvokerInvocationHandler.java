
package com.tc.trident.support.dubbo;

import java.lang.reflect.InvocationHandler;
import java.lang.reflect.Method;

import com.alibaba.dubbo.rpc.Invoker;
import com.alibaba.dubbo.rpc.RpcInvocation;
import com.tc.trident.core.StatContext;
import com.tc.trident.core.Transaction;
import com.tc.trident.util.ReflectionUtils;

/**
 * TODO 类的功能描述。
 *
 * @author kozz.gaof
 * @date Jan 11, 2015 10:11:35 PM
 * @id $Id$
 */
public class TridentInvokerInvocationHandler implements InvocationHandler {
    
    private final Invoker<?> invoker;
    
    public TridentInvokerInvocationHandler(Invoker<?> handler) {
    
        this.invoker = handler;
    }
    
    public Object invoke(Object proxy, Method method, Object[] args) throws Throwable {
    
        String methodName = method.getName();
        Class<?>[] parameterTypes = method.getParameterTypes();
        if (method.getDeclaringClass() == Object.class) {
            return method.invoke(invoker, args);
        }
        if ("toString".equals(methodName) && parameterTypes.length == 0) {
            return invoker.toString();
        }
        if ("hashCode".equals(methodName) && parameterTypes.length == 0) {
            return invoker.hashCode();
        }
        if ("equals".equals(methodName) && parameterTypes.length == 1) {
            return invoker.equals(args[0]);
        }
        
        if (StatContext.currentContext() != null) {
            
            Transaction t = new Transaction(ReflectionUtils.getCanonicalName(method));
            try {
                t.begin();
                Object o = invoker.invoke(new RpcInvocation(method, args)).recreate();
                t.setSuccess(true);
                return o;
            } catch (Throwable te) {
                t.setSuccess(false);
                throw te;
            } finally {
                t.submit();
            }
        } else {
            return invoker.invoke(new RpcInvocation(method, args)).recreate();
        }
        
    }
}
