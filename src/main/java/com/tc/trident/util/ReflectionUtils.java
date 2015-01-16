
package com.tc.trident.util;

import java.lang.reflect.Method;

/**
 *
 * @author kozz.gaof
 * @date Jan 13, 2015 4:08:27 PM
 * @id $Id$
 */
public class ReflectionUtils {
    
    public static String getCanonicalName(Method m) {
    
        StringBuilder sb = new StringBuilder();
        sb.append(m.getDeclaringClass().getCanonicalName());
        sb.append(".");
        sb.append(m.getName());
        sb.append('(');
        Class<?>[] params = m.getParameterTypes(); // avoid clone
        for (int j = 0; j < params.length; j++) {
            sb.append(getTypeName(params[j]));
            if (j < (params.length - 1))
                sb.append(',');
        }
        sb.append(')');
        return sb.toString();
    }
    
    /*
     * Utility routine to paper over array type names
     */
    static String getTypeName(Class<?> type) {
    
        if (type.isArray()) {
            try {
                Class<?> cl = type;
                int dimensions = 0;
                while (cl.isArray()) {
                    dimensions++;
                    cl = cl.getComponentType();
                }
                StringBuffer sb = new StringBuffer();
                sb.append(cl.getName());
                for (int i = 0; i < dimensions; i++) {
                    sb.append("[]");
                }
                return sb.toString();
            } catch (Throwable e) { /* FALLTHRU */
            }
        }
        return type.getName();
    }
}
