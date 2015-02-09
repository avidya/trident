
package com.tc.trident.agent;

import java.io.BufferedReader;
import java.io.FileNotFoundException;
import java.io.FileReader;
import java.io.IOException;
import java.lang.instrument.Instrumentation;
import java.util.Collections;
import java.util.HashSet;
import java.util.Set;

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
    // regex of target packages can be specified by args, the syntax is:
    // -javaagent:/PATH/TO/AGENT/trident.jar=/PATH/TO/FILTER&/PATH/TO/UNFILTER
    @SuppressWarnings("unchecked")
    public static void main(String args, Instrumentation inst) {
    
        if (args == null || args.trim().length() == 0) {
            inst.addTransformer(new ProfilerTransformer(Collections.EMPTY_SET, Collections.EMPTY_SET), true);
        } else {
            String[] files = args.split("\\&");
            if (files.length != 2) {
                System.err.println("==========> Wrong -javagent options! Correct form is: -javaagent:/PATH/TO/AGENT/trident.jar=/PATH/TO/FILTER&/PATH/TO/UNFILTER");
                System.exit(1);
            }
            inst.addTransformer(new ProfilerTransformer(loadConfig(files[0]), loadConfig(files[1])), true);
        }
    }
    
    public static Set<String> loadConfig(String filename) {
    
        BufferedReader br = null;
        HashSet<String> packages = new HashSet<String>();
        try {
            br = new BufferedReader(new FileReader(filename));
            for (String line = br.readLine(); line != null; line = br.readLine()) {
                packages.add(line);
            }
            return packages;
        } catch (FileNotFoundException e) {
            e.printStackTrace();
            return packages;
        } catch (IOException e) {
            e.printStackTrace();
            return packages;
        } finally {
            if (br != null) {
                try {
                    br.close();
                } catch (IOException e) {
                    e.printStackTrace();
                }
            }
        }
    }
}
