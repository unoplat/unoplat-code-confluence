package com.unoplat.codeunderstanding;

import java.util.ArrayList;

import com.google.gson.Gson;

import chapi.ast.javaast.JavaAnalyser;
import chapi.domain.core.CodeContainer;
import chapi.domain.core.CodeDataStruct;
/**
 * Hello world!
 *
 */
public class App 
{
    public static void main( String[] args )
    {
        JavaAnalyser javaAnalyser = new JavaAnalyser();
        CodeContainer codeContainer =  javaAnalyser.identFullInfo("public class NetworkClient {\n    \n    private NetworkService networkService;\n    \n    public NetworkClient(NetworkService networkService) {\n        this.networkService = networkService;\n    }\n\n    public void fetchDataAndPrint(String url) {\n        System.out.println(\"Fetching data from: \" + url);\n        String result = networkService.fetchData(url);\n        System.out.println(\"Received: \" + result);\n    }\n\n    public static void main(String[] args) {\n        NetworkService service = new SimpleNetworkService();\n        NetworkClient client = new NetworkClient(service);\n        client.fetchDataAndPrint(\"http://example.com/api/data\");\n    }\n}\n", "NetworkClient.java",new ArrayList<String>() , new ArrayList<CodeDataStruct>());

           Gson gson = new Gson();

        // Convert the CodeContainer object to JSON
        String json = gson.toJson(codeContainer);

        System.out.println(json);
        
    }
}
