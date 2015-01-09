
package com.tc.trident.store;

import java.io.BufferedWriter;
import java.io.File;
import java.io.FileWriter;
import java.io.IOException;
import java.io.PrintWriter;

import com.tc.trident.core.StatContext;
import com.tc.trident.core.StatInfo;
import com.tc.trident.core.Transaction;
import com.tc.trident.core.TridentException;

/**
 * Store StatInfo into plain text file.
 *
 * @author kozz.gaof
 * @date Dec 12, 2014 7:42:06 PM
 * @id $Id$
 */
public class SimpleFileStatStore extends AbstractAsyncStatStore {
    
    private static final String STAT_FILE = "monitor.stat";
    
    private static final String[] PREFIX = {
            "",
            "  ",
            "    ",
            "      ",
            "        ",
            "          ",
            "            ",
            "              " };
    
    private PrintWriter pw;
    
    @Override
    void doStore(StatInfo statInfo) {
    
        StatContext sc = (StatContext) statInfo;
        Transaction t = sc.currentTransaction();
        if (pw != null) {
            depthFirstPrint(t, 0);
        }
        pw.println();
        pw.flush();
    }
    
    void depthFirstPrint(Transaction t, int depth) {
    
        pw.print(PREFIX[depth > PREFIX.length - 1 ? PREFIX.length - 1 : depth]);
        pw.println(t);
        if (t.getChildTransactions() != null) {
            for (Transaction child : t.getChildTransactions()) {
                depthFirstPrint(child, depth + 1);
            }
        }
    }
    
    @Override
    public void close() throws TridentException {
    
        pw.close();
        
    }
    
    @Override
    public void init() throws TridentException {
    
        try {
            pw = new PrintWriter(new BufferedWriter(new FileWriter(new File(STAT_FILE))));
        } catch (IOException e) {
            throw new TridentException("Failed to open stat file, file location: " + STAT_FILE, e);
        }
    }
    
}
