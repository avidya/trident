
package com.tc.trident.util;

import java.net.InetAddress;

/**
 * Class for retrieving host related information, such as hostname, ip address //etc
 *
 * @author kozz.gaof
 * @date Jan 8, 2015 2:51:33 PM
 * @id $Id$
 */
public class HostUtils {
    
    private static final String LOOP_BACK = "127.0.0.1";
    
    private static final String UNKNOWN = "UNKNOWN";
    
    public static String getLocalHostName() {
    
        String hostName;
        try {
            InetAddress address = InetAddress.getLocalHost();
            hostName = address.getHostName();
        } catch (Exception ex) {
            ex.printStackTrace();
            hostName = UNKNOWN;
        }
        return hostName;
    }
    
    /**
     * Get the first non-loopback address according to the hostname
     *
     * @return IP ADDRESS
     */
    public static String getHostIP() {
    
        try {
            final String hostName = getLocalHostName();
            final InetAddress[] addresses = InetAddress.getAllByName(hostName);
            for (InetAddress address : addresses) {
                final String ip = address.getHostAddress();
                if (ip.matches("^(\\d{1,3}\\.){3}\\d{1,3}$") && !LOOP_BACK.equals(ip)) {
                    return ip;
                }
            }
            return UNKNOWN;
        } catch (Exception ex) {
            ex.printStackTrace();
            return UNKNOWN;
        }
    }
    
}
