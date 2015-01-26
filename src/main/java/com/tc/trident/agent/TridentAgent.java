
package com.tc.trident.agent;

import java.lang.instrument.Instrumentation;

/**
 * the entry point of the -javaagent.
 *
 * @author kozz.gaof
 * @date Jan 6, 2015 2:35:28 PM
 * @id $Id$
 */
public class TridentAgent {
    
    public static void premain(String args, Instrumentation inst) {
    
        main(args, inst);
    }
    
    // this separate main() may also be invoked from agentmain() in future.
    public static void main(String args, Instrumentation inst) {
    
        inst.addTransformer(new ProfilerTransformer(), true);
    }
}
