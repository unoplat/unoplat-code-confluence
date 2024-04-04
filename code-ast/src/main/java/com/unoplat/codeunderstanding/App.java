package com.unoplat.codeunderstanding;

import java.io.FileWriter;
import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Paths;
import java.util.ArrayList;

import org.stringtemplate.v4.ST;

import com.google.gson.Gson;

import chapi.ast.javaast.JavaAnalyser;
import chapi.domain.core.CodeContainer;
import chapi.domain.core.CodeDataStruct;

/**
 * Hello world!
 *
 */
public class App {
    public static void main(String[] args) {
        JavaAnalyser javaAnalyser = new JavaAnalyser();
        // Read file called NetworkClient.java and pass as a string to identFullInfo
        String code = new String();
        try {
            code = new String(Files.readAllBytes(Paths.get("NetworkClient.java")));
        } catch (IOException e) {
            e.printStackTrace();
        }
        CodeContainer codeContainer = javaAnalyser.identFullInfo(code, "NetworkClient.java", new ArrayList<String>(),
                new ArrayList<CodeDataStruct>());

        Gson gson = new Gson();

        // Convert the CodeContainer object to JSON
        String json = gson.toJson(codeContainer);

        try (FileWriter file = new FileWriter("output.json")) {
            file.write(json);
            System.out.println("Successfully Copied JSON Object to File...");
            System.out.println("\nJSON Object: " + json);
        } catch (IOException e) {
            e.printStackTrace();
        }

    }
}
