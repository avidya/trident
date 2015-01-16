#!/bin/bash
# scripts to genenrate pom.xml
#
# author: kozz
# date: 2015/01/13

params="$@"
TEMPLATE=pom.in
OUTPUT=pom.xml

wd=0
wt=0
wc=0
[[ $params == *with_dubbo* ]] && wd=1 
[[ $params == *with_trinity* ]] && wt=1 
[[ $params == *with_cat* ]] && wc=1 


[[ $((wd+wt+wc)) -eq 0 ]] && {
    echo '>>> You can also add with_dubbo | with_trinity | with_cat parameter to this script to augmenting functionality! :)'
    echo ">>> ./pom_gen.sh [with_dubbo] [with_trinity] [with_cat]"
    echo 
}

dependencies=
[[ $wt -eq 1 ]] && {
    dependencies="$dependencies\n\
    <dependency>\n\
      <groupId>com.tc.mw</groupId>\n\
      <artifactId>trinity</artifactId>\n\
      <version>1.2-SNAPSHOT</version>\n\
      <scope>provided</scope>\n\
    </dependency>\n"
}

[[ $wd -eq 1 ]] && {
    dependencies="$dependencies\n\
    <dependency>\n\
      <groupId>com.alibaba</groupId>\n\
      <artifactId>dubbo</artifactId>\n\
      <version>2.4.9</version>\n\
      <scope>provided</scope>\n\
    </dependency>\n"
}

[[ $wc -eq 1 ]] && {
    dependencies="$dependencies\n\
    <dependency>\n\
      <groupId>com.dianping.cat</groupId>\n\
      <artifactId>cat-core</artifactId>\n\
      <version>0.4.1</version>\n\
      <exclusions>\n\
        <exclusion>\n\
          <groupId>com.site.common</groupId>\n\
          <artifactId>lookup</artifactId>\n\
        </exclusion>\n\
        <exclusion>\n\
          <groupId>org.jboss.netty</groupId>\n\
          <artifactId>netty</artifactId>\n\
        </exclusion>\n\
      </exclusions>\n\
    </dependency>\n"
}

#echo $dependencies
sed -r "s^#_DEPENDENCY_PLACEHOLDER_#^$dependencies^" $TEMPLATE > $OUTPUT

[[ $wt -eq 1 ]] && {
    sed -r '/^\s+<exclude>\*\*\/com.tc.trinity.core.spi.Configurable<\/exclude>/d' -i $OUTPUT
    sed -r '/^\s+<sourceExclude>\*\*\/TrinityConfiguration.java<\/sourceExclude>/d' -i $OUTPUT
    sed -r '/^\s+<exclude>\*\*\/TrinityConfiguration.java<\/exclude>/d' -i $OUTPUT
}

[[ $wd -eq 1 ]] && {
    sed -r '/^\s+<exclude>\*\*\/com.alibaba.dubbo.rpc.ProxyFactory<\/exclude>/d' -i $OUTPUT
    sed -r '/^\s+<sourceExclude>\*\*\/TridentProxyFactory.java<\/sourceExclude>/d' -i $OUTPUT
    sed -r '/^\s+<sourceExclude>\*\*\/TridentInvokerInvocationHandler.java<\/sourceExclude>/d' -i $OUTPUT
    sed -r '/^\s+<exclude>\*\*\/TridentProxyFactory.java<\/exclude>/d' -i $OUTPUT
    sed -r '/^\s+<exclude>\*\*\/TridentInvokerInvocationHandler.java<\/exclude>/d' -i $OUTPUT
}

[[ $wc -eq 1 ]] && {
    sed -r '/^\s+<sourceExclude>\*\*\/StatCollector.java<\/sourceExclude>/d' -i $OUTPUT
    sed -r '/^\s+<sourceExclude>\*\*\/HeartBeat.java<\/sourceExclude>/d' -i $OUTPUT
    sed -r '/^\s+<exclude>\*\*\/StatCollector.java<\/exclude>/d' -i $OUTPUT
    sed -r '/^\s+<exclude>\*\*\/HeartBeat.java<\/exclude>/d' -i $OUTPUT
}

echo '>> Complete!'
echo ">> A new pom.xml has already been generated according to the given parameters"

