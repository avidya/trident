
package com.tc.trident.agent;

import java.lang.instrument.Instrumentation;

/**
 * Agent入口
 *
 * @author kozz.gaof
 * @date Jan 6, 2015 2:35:28 PM
 * @id $Id$
 */
public class TridentAgent {
    
    public static void premain(String args, Instrumentation inst) {
    
        main(args, inst);
    }
    
    // 单独抽离的main是为了以后可能实现的agentmain调用方便考虑
    public static void main(String args, Instrumentation inst) {
        inst.addTransformer(new ProfilerTransformer(), true);
    }
}
