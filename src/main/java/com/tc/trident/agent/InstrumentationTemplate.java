
package com.tc.trident.agent;

/**
 * Code Template
 *
 * @author kozz.gaof
 * @date Jan 7, 2015 5:28:16 PM
 * @id $Id$
 */
public interface InstrumentationTemplate {
    
    static final String BEFORE_EXECUTION = "if(com.tc.trident.core.StatContext.currentContext() != null){"
            + "com.tc.trident.core.Transaction t = new com.tc.trident.core.Transaction(\"%s\", null);"
            + "t.begin();"
            + "}";
    
    static final String AFTER_EXECUTION = "com.tc.trident.core.StatContext s = com.tc.trident.core.StatContext.currentContext();"
            + "if(s != null){"
            + "com.tc.trident.core.Transaction t = s.currentTransaction();"
            + "t.setSuccess(true);"
            + "}";
    
    static final String EXCEPTION_BLOCK = "{com.tc.trident.core.StatContext s = com.tc.trident.core.StatContext.currentContext();"
            + "if(s != null){"
            + "com.tc.trident.core.Transaction t = s.currentTransaction();"
            + "t.setSuccess(false);"
            + "}"
            + "throw $e;"
            + "}";
    
    static final String FINALLY_BLOCK = "com.tc.trident.core.StatContext s = com.tc.trident.core.StatContext.currentContext();"
            + "if(s != null){"
            + "com.tc.trident.core.Transaction t = s.currentTransaction();"
            + "t.submit();"
            + "}";
    
}
