
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
import java.util.HashSet;
import java.util.Set;

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
    
    public static final HashSet<String> MATCH_PACKAGE = new HashSet<String>();
    
    public static final HashSet<String> UNMATCH_PACKAGE = new HashSet<String>();
    static {
        MATCH_PACKAGE.add("^com/tc/.*");
        MATCH_PACKAGE.add("^com/tcmc/.*");
        MATCH_PACKAGE.add("^info/kozz/.*");
        
        UNMATCH_PACKAGE.add("^com/tc/trident/.*");
        UNMATCH_PACKAGE.add("^com/tc/trinity/.*");
        UNMATCH_PACKAGE.add(".*BySpringCGLIB.*");
        UNMATCH_PACKAGE.add(".*ByCGLIB.*");
    }
    
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
    
    public ProfilerTransformer(Set<String> matchPackage, Set<String> unmatchPackage){
        if(matchPackage != null && matchPackage.size() > 0){
            MATCH_PACKAGE.clear();
            MATCH_PACKAGE.addAll(matchPackage);
        }
        if(unmatchPackage != null && unmatchPackage.size() > 0){
            UNMATCH_PACKAGE.clear();
            UNMATCH_PACKAGE.addAll(unmatchPackage);
        }
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
