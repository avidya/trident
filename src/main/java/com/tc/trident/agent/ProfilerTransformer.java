
package com.tc.trident.agent;

import static com.tc.trident.agent.InstrumentationTemplate.AFTER_EXECUTION;
import static com.tc.trident.agent.InstrumentationTemplate.BEFORE_EXECUTION;
import static com.tc.trident.agent.InstrumentationTemplate.EXCEPTION_BLOCK;
import static com.tc.trident.agent.InstrumentationTemplate.FINALLY_BLOCK;

import java.io.IOException;
import java.lang.instrument.ClassFileTransformer;
import java.lang.instrument.IllegalClassFormatException;
import java.lang.reflect.Modifier;
import java.security.ProtectionDomain;

import javassist.CannotCompileException;
import javassist.ClassPool;
import javassist.CtBehavior;
import javassist.CtClass;
import javassist.LoaderClassPath;
import javassist.NotFoundException;

/**
 * proformance monitor profiler
 *
 * @author kozz.gaof
 * @date Jan 6, 2015 3:11:14 PM
 * @id $Id$
 */
public class ProfilerTransformer implements ClassFileTransformer {
    
    public static final String[] MATCH_PACKAGE = {
            "^com/tc/.*",
            "^com/tcmc/.*",
            "^info/kozz/.*"
    };
    
    public static final String[] UNMATCH_PACKAGE = {
            "^com/tc/trident/.*",
            "^com/tc/trinity/.*",
            ".*BySpringCGLIB.*",
            ".*ByCGLIB.*"
    };
    
    private boolean match(String className) {
    
        for (String prefix1 : MATCH_PACKAGE) {
            if (className.matches(prefix1)) {
                for (String prefix2 : UNMATCH_PACKAGE) {
                    if (className.matches(prefix2)) {
                        return false;
                    }
                }
                return true;
            }
        }
        return false;
    }
    
    private String normalizeClassPath(String className) {
    
        return className.replaceAll("/", ".");
    }
    
    @Override
    public byte[] transform(ClassLoader loader, String className, Class<?> classBeingRedefined, ProtectionDomain protectionDomain, byte[] classfileBuffer) throws IllegalClassFormatException {
    
        if (match(className)) {
            System.out.println(">>>>>>>>>>> " + className + " is gonna to be transformed!");
            String normalClassName = normalizeClassPath(className);
            try {
                ClassPool pool = ClassPool.getDefault();
                pool.appendClassPath(new LoaderClassPath(loader));
                CtClass cc = pool.get(normalClassName);
                CtClass throwable = pool.get("java.lang.Throwable");
                // leave Interface untouched
                if (cc.isInterface()) {
                    return classfileBuffer;
                }
                for (CtBehavior behavior : cc.getDeclaredBehaviors()) {
                    // skip abstract method
                    if (Modifier.isAbstract(behavior.getModifiers())) {
                        continue;
                    }
                    behavior.insertBefore(String.format(BEFORE_EXECUTION, behavior.getLongName()));
                    behavior.insertAfter(AFTER_EXECUTION);
                    behavior.addCatch(EXCEPTION_BLOCK, throwable);
                    behavior.insertAfter(FINALLY_BLOCK, true);
                }
                return cc.toBytecode();
            } catch (NotFoundException e) {
                System.err.println(">>>>>>>>>>> Cannot load class " + className + " in ClassLoader: " + loader);
                e.printStackTrace();
            } catch (CannotCompileException e) {
                System.err.println(">>>>>>>>>>> Cannot compile " + className + " in ClassLoader: " + loader);
                e.printStackTrace();
            } catch (IOException e) {
                e.printStackTrace();
            }
        }
        
        return classfileBuffer;
    }
}
